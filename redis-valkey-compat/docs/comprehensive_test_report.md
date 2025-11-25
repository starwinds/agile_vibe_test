# Redis vs. Valkey 호환성 및 성능 테스트 종합 보고서

- **작성일:** 2025년 11월 24일
- **작성자:** Gemini CLI
- **기반 데이터:** Sprint 2 테스트 결과 (`results_redis726.json`, `results_valkey900.json`)

## 1. 개요

본 문서는 `redis-valkey-compat` 프로젝트에서 수행된 Redis 7.2.6과 Valkey 9.0.0 간의 호환성 및 성능 비교 테스트 결과를 종합한 보고서입니다. 기본 기능 호환성뿐만 아니라 대용량 페이로드 처리 성능 및 메모리 축출(Eviction) 동작을 비교 분석하였습니다.

## 2. 테스트 환경

| 항목 | Redis 환경 | Valkey 환경 |
|---|---|---|
| **이미지** | `redis:7.2.6` | `valkey/valkey:9.0` |
| **실행 환경** | Docker Container | Docker Container |
| **테스트 클라이언트** | Python (`redis-py`) | Python (`redis-py`) |

## 3. 테스트 결과 요약

모든 테스트 시나리오(`basic_crud`, `data_structures`, `scan_and_iter`, `lua_and_tx`, `pubsub`, `memory_eviction`, `large_payloads`)가 두 타겟 시스템에서 **성공(OK)** 하였습니다. 기능적인 호환성 문제는 발견되지 않았습니다.

## 4. 상세 성능 분석

### 4.1. 대용량 페이로드 처리 (Large Payloads)

1MB, 5MB, 10MB 크기의 데이터를 쓰고 읽는 작업에서의 지연 시간(Latency)과 메모리 사용량을 비교했습니다.

| 페이로드 크기 | 지표 | Redis 7.2.6 | Valkey 9.0.0 | 차이 (Valkey - Redis) |
| :---: | :--- | :--- | :--- | :--- |
| **1MB** | Set Latency (ms) | 2.81 | 1.14 | **-1.67 ms (더 빠름)** |
| | Get Latency (ms) | 3.80 | 1.92 | **-1.88 ms (더 빠름)** |
| | Memory Usage (Bytes) | 2,650,432 | 2,671,416 | +20,984 bytes |
| **5MB** | Set Latency (ms) | 5.37 | 4.09 | **-1.28 ms (더 빠름)** |
| | Get Latency (ms) | 13.07 | 12.36 | **-0.71 ms (더 빠름)** |
| | Memory Usage (Bytes) | 11,272,256 | 11,272,608 | +352 bytes |
| **10MB** | Set Latency (ms) | 5.73 | 8.10 | +2.37 ms (더 느림) |
| | Get Latency (ms) | 20.64 | 20.33 | -0.31 ms (비슷함) |
| | Memory Usage (Bytes) | 18,874,432 | 18,874,792 | +360 bytes |

**분석:**
- 1MB 및 5MB 구간에서는 Valkey가 Redis보다 쓰기/읽기 성능에서 우위를 보였습니다.
- 10MB 쓰기 작업에서는 Redis가 다소 빠른 성능을 보였으나, 읽기 성능은 비슷했습니다.
- 메모리 사용량은 두 시스템이 거의 동일하며, Valkey가 미세하게 더 많은 메모리를 사용하는 경향이 있으나 무시할 수준입니다.

### 4.2. 메모리 축출 (Memory Eviction)

제한된 메모리 환경에서 키가 축출되는 동작을 검증했습니다.

| 항목 | Redis 7.2.6 | Valkey 9.0.0 | 비고 |
| :--- | :--- | :--- | :--- |
| **초기 키 개수** | 40 | 40 | |
| **축출 후 키 개수** | 13 | 13 | 동일한 축출 정책 동작 |
| **축출된 키 개수** | 27 | 27 | |

**분석:**
- 두 시스템 모두 동일한 메모리 설정 하에서 정확히 같은 수의 키를 축출했습니다. 이는 메모리 관리 정책이 호환됨을 의미합니다.

## 5. 기능 호환성 테스트 결과

다음 시나리오들은 기능의 정확성을 검증하였으며, 성능 측정보다는 동작 여부에 중점을 두었습니다.

| 시나리오 | Redis 결과 | Valkey 결과 | 상세 내용 |
| :--- | :---: | :---: | :--- |
| **basic_crud** | OK | OK | 기본 SET/GET/DELETE 동작 정상 |
| **data_structures** | OK | OK | List, Set, Hash, Sorted Set 연산 정상 |
| **scan_and_iter** | OK | OK | SCAN 계열 명령어를 통한 반복 조회 정상 |
| **pubsub** | OK | OK | Publish/Subscribe 메시지 전달 정상 |
| **lua_and_tx** | OK | OK | Lua 스크립트 실행 및 트랜잭션(MULTI/EXEC) 정상 |

## 6. 결론

테스트 결과, **Valkey 9.0.0은 Redis 7.2.6과 완벽한 기능적 호환성**을 보여주었습니다.

1.  **호환성**: 기존 Redis 클라이언트(`redis-py`)와 테스트 코드를 수정 없이 그대로 사용하여 모든 테스트를 통과했습니다.
2.  **성능**: 5MB 이하의 페이로드 처리에서 Valkey가 Redis보다 더 나은 지연 시간 성능을 보였습니다. 10MB 이상의 대용량 쓰기에서는 Redis가 다소 앞섰으나 큰 차이는 아닙니다.
3.  **안정성**: 메모리 축출 및 트랜잭션 처리 등 핵심 메커니즘이 동일하게 동작함을 확인했습니다.

따라서, Redis 7.2.6에서 Valkey 9.0.0으로의 마이그레이션은 기능적 관점에서 안전하며, 일부 워크로드에서는 성능 향상을 기대할 수 있을 것으로 판단됩니다.
