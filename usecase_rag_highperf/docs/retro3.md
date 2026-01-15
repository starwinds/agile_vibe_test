# Sprint 3 Retrospective: High-Performance RAG Tools & Benchmark

## 1. 스프린트 개요 (Overview)
*   **목표**: Single Tenant 환경에서의 대규모 데이터 처리 및 성능 벤치마크를 위한 도구 세트 구축.
*   **기간**: 2026-01-15 (1일간 집중 개발)
*   **주요 성과**:
    *   `generate_dataset.py`: 수천 건의 문서/청크 및 Outbox 이벤트 고속 생성기 구현.
    *   `generate_queries.py`: 실제 DB 데이터를 기반으로 한 4가지 전략(Semantic, Keyword, Hybrid, Freshness)의 질의 생성기 구현.
    *   `bench.py` & `metrics.py`: Latency(P50/P95/P99) 및 QPS 측정을 위한 비동기 벤치마크 도구 구현.
    *   `manual_test_sprint3_guide.md`: 사용자 테스트를 위한 단계별 가이드 문서화.

## 2. 잘된 점 (Keep)
*   **비동기 최적화**: `bench.py`에서 `asyncio.Semaphore`와 비동기 클라이언트(`redis.asyncio`, `psycopg.AsyncConnection`)를 사용하여 높은 동시성(Concurrency) 테스트 환경을 구축함.
*   **유연한 테스트 환경**: `mock-embedding` 옵션을 도입하여 Ollama 등 외부 LLM 서비스 없이도 검색 엔진(Valkey) 및 DB I/O 성능을 독립적으로 측정할 수 있게 함.
*   **실제 시나리오 반영**: 단순 랜덤 데이터가 아닌, `faker`를 활용한 텍스트 생성과 Outbox 이벤트를 통한 데이터 변경 시나리오(Update/Delete)를 포함하여 실제 운영 환경에 근접한 테스트가 가능해짐.

## 3. 아쉬운 점 (Problem)
*   **임베딩 병목**: 실제 임베딩 생성(`no-mock-embedding`) 모드 사용 시, Ollama API의 처리 속도가 전체 시스템 벤치마크의 병목이 됨. 이는 벤치마크 도구의 문제가 아닌 임베딩 인프라의 한계임.
*   **데이터 일관성**: `generate_dataset.py`에서 생성된 `outbox_events`가 실제 `indexer.py`에 의해 모두 처리될 때까지 대기하는 로직이 벤치마크 도구 내에 포함되지 않아, 사용자가 수동으로 인덱싱 완료를 확인해야 함.

## 4. 개선 및 고도화 사항 (Try/Future)
*   **자동 인덱싱 확인 (Indexer Sync Wait)**: 벤치마크 시작 전, `outbox_events`의 `PENDING` 상태가 0이 될 때까지 대기하는 자동화 스크립트 추가.
*   **임베딩 캐싱**: 동일한 질의에 대해 중복 임베딩 생성을 방지하기 위한 캐싱 레이어 검토.
*   **분산 부하 테스트**: 단일 클라이언트의 Python 프로세스 한계를 넘어서기 위해, 여러 노드에서 부하를 발생시키는 Distributed Benchmarking 기능 검토.
*   **시각화 리포트**: JSON 형태의 결과물을 차트(Latency Distribution, QPS Over Time)로 시각화하는 웹 대시보드 또는 정적 HTML 리포트 생성 기능.

## 5. 결론 (Conclusion)
Sprint 3를 통해 RAG 시스템의 한계를 시험하고 최적화 포인트를 찾을 수 있는 정량적 측정 도구를 성공적으로 확보함. 이를 통해 향후 대규모 엔터프라이즈 환경으로의 확장성을 검증할 수 있는 기반이 마련됨.
