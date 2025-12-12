# Valkey VectorDBBench 수동 벤치마크 가이드

이 문서는 Valkey VectorDBBench 확장을 사용하여 다양한 배포 환경(Standalone, Cluster, HA)에서 벤치마크를 수동으로 수행하는 방법을 설명합니다.

## 1. 사전 준비 (Prerequisites)

### 1.1 필수 도구
- **Docker & Docker Compose**: Valkey 인스턴스 실행용
- **Python 3.10+**: 벤치마크 클라이언트 실행용
- **Git**: 코드 저장소 복제용

### 1.2 환경 설정
```bash
# 저장소 복제 (이미 완료된 경우 생략)
git clone https://github.com/starwinds/agile_vibe_test.git
cd agile_vibe_test/valkey-vector-benchmark/VectorDBBench

# Python 가상 환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
pip install valkey  # valkey-py 클라이언트 설치
```

## 2. 벤치마크 구성 (Configuration)

벤치마크 설정은 `valkey_bench_config.yaml` 파일에서 관리합니다.
테스트하려는 시나리오에 맞춰 `cases` 섹션의 주석을 해제하거나 수정해야 합니다.

- **Standalone**: `deployment_type: STANDALONE` (기본값)
- **Cluster**: `deployment_type: CLUSTER`
- **HA (Sentinel)**: `deployment_type: SENTINEL`

## 3. 시나리오별 실행 방법

### 3.1 Standalone 벤치마크

가장 기본적인 단일 노드 구성입니다.

1.  **Valkey 실행**:
    ```bash
    # 로컬에 Valkey(Vector Search 포함) 실행
    docker run -d --name valkey-vector-bench -p 6379:6379 valkey/valkey-bundle:latest
    ```

2.  **Config 설정 (`valkey_bench_config.yaml`)**:
    - `case_id: 1` (HNSW) 또는 `case_id: 2` (FLAT) 활성화.
    - `db_config`의 `host`, `port` 확인 (기본값: 127.0.0.1:6379).

3.  **벤치마크 실행**:
    ```bash
    vectordbbench test --config-file valkey_bench_config.yaml
    ```

4.  **정리**:
    ```bash
    docker stop valkey-vector-bench && docker rm valkey-vector-bench
    ```

### 3.2 Cluster 벤치마크

6개의 노드(3 Master, 3 Replica)로 구성된 클러스터 환경입니다.

1.  **Cluster 실행**:
    ```bash
    docker-compose -f docker-compose.benchmark-cluster.yml up -d
    
    # 초기화 완료 대기 (로그 확인)
    docker logs -f cluster-initializer
    # ">>> Valkey Cluster initialized." 메시지가 나오면 Ctrl+C로 종료
    ```

2.  **Config 설정 (`valkey_bench_config.yaml`)**:
    - `case_id: 3` (Cluster) 활성화.
    - 다른 케이스는 주석 처리 권장.

3.  **벤치마크 실행**:
    ```bash
    vectordbbench test --config-file valkey_bench_config.yaml
    ```

4.  **정리**:
    ```bash
    docker-compose -f docker-compose.benchmark-cluster.yml down
    ```

### 3.3 HA (Sentinel) 벤치마크

Master 1개, Replica 2개, Sentinel 3개로 구성된 고가용성 환경입니다.

1.  **HA 실행**:
    ```bash
    docker-compose -f docker-compose.benchmark-ha.yml up -d
    
    # 상태 확인
    docker-compose -f docker-compose.benchmark-ha.yml ps
    ```

2.  **Config 설정 (`valkey_bench_config.yaml`)**:
    - `case_id: 4` (HA) 활성화.
    - `service_name`이 `myvalkey`인지 확인.

3.  **벤치마크 실행**:
    ```bash
    vectordbbench test --config-file valkey_bench_config.yaml
    ```

4.  **정리**:
    ```bash
    docker-compose -f docker-compose.benchmark-ha.yml down
    ```

## 4. 결과 확인

벤치마크가 완료되면 터미널에 요약 결과가 출력되며, 상세 결과는 `vectordb_bench/results/` 디렉토리에 저장될 수 있습니다 (설정에 따라 다름).

주요 성능 지표:
- **QPS (Queries Per Second)**: 초당 처리량
- **Latency**: 응답 속도 (Avg, P99)
- **Recall**: 검색 정확도

## 5. 트러블슈팅

- **Connection Error**: Docker 컨테이너가 정상적으로 실행 중인지 확인하세요. (`docker ps`)
- **Import Error**: `valkey` 패키지가 설치되어 있는지 확인하세요. (`pip list | grep valkey`)
- **Aborted**: 부하가 너무 높으면 테스트가 중단될 수 있습니다. `valkey_bench_config.yaml`에서 `concurrency` 설정을 낮추거나 `dataset` 크기를 조절해 보세요.
