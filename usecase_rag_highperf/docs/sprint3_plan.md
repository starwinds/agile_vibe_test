# Sprint 3 Plan: High Performance RAG Tools & Benchmark

## 1. 개요 (Overview)
*   **목표**: Single Tenant 환경에서의 대규모 데이터 처리 및 성능 벤치마크를 위한 도구 개발.
*   **기간**: 2026-01-15 ~ 2026-01-21 (1주)
*   **주요 산출물**:
    *   데이터 생성기 (`generate_dataset.py`)
    *   질의 생성기 (`generate_queries.py`)
    *   벤치마크 도구 (`bench.py`, `metrics.py`)
    *   벤치마크 결과 리포트

## 2. 스프린트 백로그 (Sprint Backlog)

| ID | Task Name | Description | Estimation | Assignee |
| :--- | :--- | :--- | :--- | :--- |
| **ADV-001** | **데이터 생성기 개발** | `app/generate_dataset.py` 구현. 대규모 코퍼스 및 Outbox 이벤트 생성. | 2 days | TBD |
| **ADV-002** | **질의 생성기 개발** | `app/generate_queries.py` 구현. 다양한 유형의 질의 및 Golden Answer 생성. | 1 day | TBD |
| **ADV-003** | **벤치마크 도구 개발** | `app/bench.py`, `app/metrics.py` 구현. Latency/QPS 측정 및 리포팅. | 2 days | TBD |
| **ADV-004** | **문서화 업데이트** | `README.md`에 도구 사용법 및 벤치마크 가이드 추가. | 0.5 day | TBD |

## 3. 상세 계획 (Detailed Plan)

> [!IMPORTANT]
> 본 계획은 `gemini-cli`의 **Auto Accept** 모드를 전제로 작성되었습니다. 각 Task는 명시된 **구현 상세(Implementation Details)**를 엄격히 준수하여 개발해야 합니다.

### 3.1 데이터 생성기 (Data Generator)
*   **Task ID**: ADV-001
*   **File**: `app/generate_dataset.py`
*   **Libraries**: `faker` (필요 시 `pip install faker` 추가), `psycopg[binary]`, `asyncio`
*   **Implementation Details**:
    1.  **CLI Args**: `argparse` 사용.
        *   `--docs`: 생성할 문서 수 (int, default: 1000)
        *   `--avg-chunks`: 문서당 평균 청크 수 (int, default: 10)
        *   `--update-rate`: 업데이트할 문서 비율 (float, default: 0.1)
        *   `--delete-rate`: 삭제할 문서 비율 (float, default: 0.05)
        *   `--seed`: 랜덤 시드 (int, default: 42)
    2.  **Logic**:
        *   `Faker`를 사용하여 `title` (sentence), `content` (paragraphs) 생성.
        *   `content`를 `\n\n` 등으로 분리하여 `chunks` 생성.
        *   **Batch Insert**: `psycopg`의 `execute_batch` 또는 `copy`를 사용하여 고속 적재.
        *   **Outbox Event**:
            *   `event_type`: `CHUNK_UPSERT` (신규/수정), `CHUNK_DELETE` (삭제)
            *   `payload`: JSON 구조. `{"doc_id": ..., "chunk_id": ..., "text": ...}`
    3.  **Output**:
        *   DB Tables: `documents`, `chunks`, `doc_acl` (default: `public`), `outbox_events` populated.
        *   File: `data/manifest.json`
            ```json
            {
              "total_docs": 1000,
              "total_chunks": 10000,
              "updated_docs": 100,
              "deleted_docs": 50
            }
            ```

### 3.2 질의 생성기 (Query Generator)
*   **Task ID**: ADV-002
*   **File**: `app/generate_queries.py`
*   **Implementation Details**:
    1.  **Query Generation Strategy** (LLM 없이 로직으로 생성):
        *   **Semantic (50%)**: `chunks` 테이블에서 랜덤 청크 선택 -> 해당 청크의 첫 문장 또는 임의의 문장을 가져와서 일부 단어를 유의어(또는 랜덤 변형)로 교체하거나 그대로 사용. (단순화: 청크의 첫 문장 사용)
        *   **Keyword (25%)**: 청크 내에서 대문자로 시작하는 단어(고유명사 추정) 또는 5글자 이상 단어 1~2개 추출.
        *   **Hybrid (20%)**: Keyword + Semantic 조합.
        *   **Freshness (5%)**: `outbox_events`에서 `CHUNK_UPSERT`된 문서 중 최신 버전을 타겟으로 위 로직 수행.
    2.  **Output Format**: `data/queries.jsonl`
        ```json
        {"query_id": "q1", "type": "semantic", "text": "...", "expected_doc_ids": [1, 5]}
        ```

### 3.3 벤치마크 도구 (Benchmark Tool)
*   **Task ID**: ADV-003
*   **File**: `app/bench.py`, `app/metrics.py`
*   **Implementation Details**:
    1.  **Architecture**:
        *   Producer-Consumer 패턴 또는 `asyncio.gather`를 이용한 Concurrent Request.
        *   `aiohttp` 또는 `asyncio` 호환 클라이언트 사용 권장 (Valkey는 `valkey-py`의 async client, Postgres는 `psycopg` async connection).
    2.  **Modes**:
        *   `valkey_knn`: `valkey_client.ft(index).search(...)` 수행 시간만 측정.
        *   `hybrid_fetch`: Search 후 반환된 ID로 Postgres `SELECT chunk_text FROM chunks WHERE ...` 수행 시간 포함.
    3.  **Metrics (`metrics.py`)**:
        *   Class `MetricsCollector`: `add_latency(ms)`, `calculate_report()`.
        *   `p50`, `p95`, `p99`는 `numpy.percentile` 또는 정렬 후 인덱싱으로 계산.
    4.  **Report**: `out/bench_{mode}_{timestamp}.json`

### 3.4 문서화 및 의존성 (Documentation & Deps)
*   **Task ID**: ADV-004
*   **File**: `README.md`, `app/requirements.txt`
*   **Details**:
    *   `app/requirements.txt`에 `faker`, `numpy` 등 누락된 의존성 추가 필수.
    *   `README.md`에 각 스크립트의 예시 커맨드(Copy-Paste 가능하도록) 명시.
    *   **Environment**: 프로젝트 루트의 기존 `.venv` 가상환경 활용.

## 4. 검증 계획 (Verification Plan)
*   **Prerequisite**: `source .venv/bin/activate` 실행.
*   **Step 1**: `pip install -r app/requirements.txt` 성공 확인.
*   **Step 2**: `python app/generate_dataset.py --docs 100` 실행 -> DB `SELECT count(*) FROM documents`가 100인지 확인.
*   **Step 3**: `python app/generate_queries.py --queries 10` 실행 -> `data/queries.jsonl` 라인 수 10 확인.
*   **Step 4**: `python app/bench.py --queries data/queries.jsonl --mode valkey_knn` 실행 -> `out/bench_*.json` 생성 확인.
