# Sprint 3 Manual Test Guide: High-Performance RAG Benchmark Tools

이 문서는 Sprint 3에서 개발된 **대규모 데이터 처리 및 성능 벤치마크 도구**를 사용자가 직접 테스트하는 방법을 안내합니다.

## 1. 개요 (Overview)

Sprint 3의 목표는 RAG 시스템의 성능을 측정하기 위한 데이터 생성, 질의 생성, 그리고 벤치마크 실행 도구를 확보하는 것입니다. 이 가이드를 통해 다음 시나리오를 검증할 수 있습니다.

1.  **Data Generation**: 수천 건의 문서와 청크를 생성하고 DB에 적재.
2.  **Indexing**: 생성된 데이터를 백그라운드에서 벡터화하여 Valkey에 적재 (Ollama 필요).
3.  **Query Generation**: 저장된 데이터를 기반으로 현실적인 테스트 질의 생성.
4.  **Benchmarking**: 다양한 모드(Vector Only, Hybrid)로 검색 성능(Latency, QPS) 측정.

## 2. 사전 준비 (Prerequisites)

*   **Docker & Docker Compose**: 실행 중이어야 합니다.
*   **Python 3.10+**: 가상환경(`.venv`)이 설정되어 있어야 합니다.
*   **Ollama**: 로컬에서 실행 중이어야 하며, `nomic-embed-text` 모델이 필요합니다.
    *   설치 및 실행: [Ollama 공식 홈페이지](https://ollama.com/)
    *   모델 다운로드: `ollama pull nomic-embed-text`

## 3. 테스트 절차 (Test Steps)

### Step 0: 환경 설정 및 의존성 설치

프로젝트 루트 디렉토리(`usecase_rag_highperf`)에서 진행합니다.

1.  **가상환경 활성화**:
    ```bash
    cd usecase_rag_highperf
    source .venv/bin/activate
    ```

2.  **최신 의존성 설치**:
    Sprint 3에서 추가된 `faker` 등의 라이브러리를 설치합니다.
    ```bash
    pip install -r app/requirements.txt
    ```

3.  **인프라 재구동 (Clean State 권장)**:
    기존 데이터를 날리고 깨끗한 상태에서 시작하려면 아래 명령어를 수행하세요. (데이터 보존이 필요하면 생략)
    ```bash
    docker compose down -v
    docker compose up -d
    ```

### Step 1: 대규모 데이터 생성 (Data Generation)

`generate_dataset.py`를 사용하여 테스트 데이터를 생성합니다. 빠른 테스트를 위해 문서를 100개만 생성해 봅니다.

*   **명령어**:
    ```bash
    python app/generate_dataset.py --docs 100 --avg-chunks 5 --update-rate 0.1
    ```
*   **옵션 설명**:
    *   `--docs 100`: 문서 100개 생성.
    *   `--avg-chunks 5`: 문서당 평균 5개의 청크.
    *   `--update-rate 0.1`: 10%의 문서에 대해 수정 이벤트 생성.
*   **예상 결과**:
    *   DB(`documents`, `chunks`, `outbox_events`)에 데이터가 적재됩니다.
    *   `data/manifest.json` 파일이 생성됩니다.

### Step 2: 인덱싱 실행 (Indexing)

생성된 데이터(`outbox_events`)를 처리하여 Valkey에 벡터 인덱스를 구축합니다.

1.  **Indexer 실행 (백그라운드 또는 별도 터미널)**:
    ```bash
    python app/indexer.py
    ```
    *   *참고: 이 과정은 Ollama의 성능에 따라 시간이 소요될 수 있습니다. (문서 100개 기준 수 분 내외)*
    *   로그에 `Indexed chunk ...` 메시지가 출력되는지 확인하세요.

2.  **데이터 적재 확인**:
    잠시 후, 처리가 완료되었는지 확인합니다. (더 이상 로그가 올라오지 않으면 중단해도 됩니다.)

### Step 3: 질의 생성 (Query Generation)

DB에 저장된 실제 텍스트 데이터를 기반으로 테스트용 질의를 생성합니다.

*   **명령어**:
    ```bash
    python app/generate_queries.py --queries 50
    ```
*   **옵션 설명**:
    *   `--queries 50`: 총 50개의 질의 생성.
*   **예상 결과**:
    *   `data/queries.jsonl` 파일이 생성됩니다.
    *   내용 예시: `{"query_id": "q1", "type": "semantic", "text": "...", "expected_doc_ids": [...]}`

### Step 4: 벤치마크 실행 (Benchmarking)

검색 성능을 측정합니다. 두 가지 모드를 테스트해 봅니다.

#### Case A: Mock Embedding (빠른 성능 측정)
Ollama를 거치지 않고 랜덤 벡터를 생성하여 Valkey 검색 속도만 측정합니다. (네트워크/DB I/O 집중 테스트)

*   **명령어**:
    ```bash
    python app/bench.py --mode valkey_knn --mock-embedding --concurrency 20
    ```
*   **예상 결과**:
    *   콘솔에 JSON 포맷의 리포트가 출력됩니다.
    *   `out/bench_valkey_knn_*.json` 파일이 생성됩니다.
    *   높은 QPS(수백~수천)가 예상됩니다.

#### Case B: Hybrid Fetch (실제 시나리오)
벡터 검색 후 Postgres에서 원본 텍스트를 조회하는 과정까지 포함합니다.

*   **명령어**:
    ```bash
    python app/bench.py --mode hybrid_fetch --mock-embedding --concurrency 10
    ```
*   **예상 결과**:
    *   Case A보다 낮은 QPS가 측정됩니다 (DB 조회 비용 포함).

#### Case C: Real Embedding (선택 사항)
실제 Ollama를 통해 질의 임베딩을 생성하여 검색합니다. (가장 느림, 정확도 테스트용)

*   **명령어**:
    ```bash
    python app/bench.py --mode valkey_knn --no-mock-embedding --concurrency 1
    ```

## 4. 결과 분석 (Result Analysis)

`out/` 디렉토리에 생성된 JSON 파일을 열어 다음 지표를 확인합니다.

*   `qps`: 초당 처리량. 높을수록 좋습니다.
*   `p95_latency`, `p99_latency`: 꼬리 응답 시간(ms). 낮을수록 안정적입니다.
*   `error_count`: 0이어야 합니다.

## 5. 문제 해결 (Troubleshooting)

*   **`Connection refused` (Ollama)**:
    *   Ollama가 실행 중인지 확인하세요 (`curl http://localhost:11434`).
    *   `indexer.py` 실행 시 에러가 발생하면 벡터가 적재되지 않아 벤치마크 결과(검색 결과 수)가 0이 될 수 있습니다.
*   **`ModuleNotFoundError`**:
    *   `pip install -r app/requirements.txt`를 다시 실행하세요.
*   **검색 결과가 0건**:
    *   `indexer.py`가 정상적으로 이벤트를 처리했는지 확인하세요.
    *   `generate_dataset.py` 실행 후 `indexer.py`를 충분한 시간 동안 실행시켜야 합니다.
