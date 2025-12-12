# Valkey 벤치마크 결과 요약 (Valkey Benchmark Result Summary)

## 1. 개요 (Overview)
본 문서는 VectorDBBench를 사용하여 수행한 Valkey Vector Search 벤치마크 결과를 요약합니다.
이번 테스트는 `valkey/valkey-bundle:latest` 이미지를 사용하여 Cluster 및 HA(Sentinel) 모드에서 수행되었습니다.

## 2. 테스트 환경 (Test Environment)
- **Valkey 버전**: `valkey/valkey-bundle:latest`
- **인스턴스 유형**: Local Docker Container
- **데이터셋**: `OpenAI-SMALL-50K` (크기: 50,000, 차원: 1536)
- **테스트 케이스**: `Performance1536D50K`

## 3. 결과 (Results)

테스트 실행 중 환경 및 설정 문제로 인해 벤치마크가 정상적으로 완료되지 않았습니다.

### 3.1 실행 결과 요약

| Deployment Type | Status | Error Message |
| :--- | :--- | :--- |
| **Cluster** | **Failed** | `AttributeError: 'dict' object has no attribute 'name'` |
| **HA (Sentinel)** | **Failed** | `ConnectionError: Error while reading from 127.0.0.1:26379 : (104, 'Connection reset by peer')` |

### 3.2 상세 분석

#### Cluster 모드 실패 원인
- **증상**: 벤치마크 실행 초기 단계에서 `AttributeError` 발생.
- **원인**: `vectordb-bench` 프레임워크와 Valkey 클라이언트 간의 설정 객체(`db_config`) 전달 과정에서 타입 불일치(Dictionary vs Object)가 발생한 것으로 추정됩니다. `new_client.py`에서 수정을 시도했으나, 프레임워크 내부의 다른 부분에서 문제가 지속되고 있습니다.

#### HA (Sentinel) 모드 실패 원인
- **증상**: Sentinel(포트 26379) 접속 시 `Connection reset by peer` 에러 발생.
- **원인**: Docker 컨테이너 내의 Sentinel이 호스트 머신에서의 연결을 거부하거나, 네트워크 설정 문제로 인해 연결이 불안정한 상태입니다. `wait_for_port` 체크는 통과했으나, 실제 클라이언트 연결 시 문제가 발생했습니다.

## 4. 결론 및 향후 계획 (Conclusion & Next Steps)

현재 환경에서는 벤치마크를 통한 성능 측정이 불가능했습니다. 다음 단계로 문제 해결을 제안합니다:

1.  **HA 네트워크 디버깅**: Sentinel 컨테이너의 로그를 분석하여 연결 거부 원인을 파악하고, `docker-compose` 네트워크 설정을 점검해야 합니다.
2.  **Cluster 클라이언트 수정**: `vectordb-bench` 프레임워크의 `TaskRunner`와 `ValkeyClient` 간의 인터페이스를 심층 분석하여 설정 객체 전달 방식을 수정해야 합니다.
3.  **재검증**: 위 문제 해결 후 벤치마크를 재수행하여 성능 데이터를 확보해야 합니다.
