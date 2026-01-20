# Sprint 4 Plan: Demo App (FastAPI + Streamlit)

## 1. 개요 (Overview)
*   **목표**: End-user가 체감할 수 있는 검색 데모 애플리케이션(FastAPI 백엔드 + Streamlit 프론트엔드) 개발.
*   **기간**: 2026-01-22 ~ 2026-01-28 (1주)
*   **주요 산출물**:
    *   Demo API (`app/demo_api/`)
    *   Streamlit UI (`app/streamlit_app/`)
    *   실행 가이드 (`README.md`)

## 2. 스프린트 백로그 (Sprint Backlog)

| ID | Task Name | Description | Estimation | Assignee |
| :--- | :--- | :--- | :--- | :--- |
| **DEMO-001** | **프로젝트 구조 및 의존성** | `app/demo_api`, `app/streamlit_app` 구조 생성 및 `requirements-demo.txt` 작성. | 0.5 day | TBD |
| **DEMO-002** | **Demo API 구현** | Semantic, Keyword, Hybrid 검색 로직 및 FastAPI 엔드포인트 구현. | 2 days | TBD |
| **DEMO-003** | **Streamlit UI 구현** | 검색 모드, 옵션 설정, 결과 표시, Preset 버튼 UI 구현. | 1.5 days | TBD |
| **DEMO-004** | **문서화** | `README.md` 업데이트 및 `manual_test_sprint4_guide.md` 작성. | 0.5 day | TBD |
| **DEMO-005** | **검색 결과 표시 개선** | 검색 결과에 원본 콘텐츠(본문) 포함 및 UI 표시 개선. | 0.5 day | TBD |
| **DEMO-006** | **Backend - Schema Update** | `chunk_embeddings` 테이블 추가 (Pattern B). | 0.5 day | TBD |
| **DEMO-007** | **Backend - Indexer Update** | Indexer 로직 확장 (PG SoR + Valkey). | 1.0 day | TBD |
| **DEMO-008** | **Backend - Rebuild Tool** | Valkey 인덱스 Rebuild 스크립트 작성. | 0.5 day | TBD |
| **DEMO-009** | **Demo API - Engine Support** | 검색 엔진 선택(`engine`) 파라미터 및 Fallback 로직 추가. | 0.5 day | TBD |
| **DEMO-010** | **Streamlit UI - Engine Selector** | UI에 엔진 선택 및 Debug 정보 표시 추가. | 0.5 day | TBD |

## 3. 상세 계획 (Detailed Plan)

> [!IMPORTANT]
> 본 계획은 `gemini-cli`의 **Auto Accept** 모드를 전제로 작성되었습니다. 각 Task는 명시된 **구현 상세(Implementation Details)**를 엄격히 준수하여 개발해야 합니다.

### 3.1 프로젝트 구조 및 의존성 (Structure & Deps)
*   **Task ID**: DEMO-001
*   **Files**:
    *   `app/demo_api/__init__.py`, `app/demo_api/settings.py`, `app/demo_api/clients.py`
    *   `app/streamlit_app/__init__.py`
    *   `requirements-demo.txt`
*   **Implementation Details**:
    *   **Dependencies**: `fastapi`, `uvicorn[standard]`, `pydantic`, `streamlit`, `httpx`, `redis`, `python-dotenv`.
    *   **Settings**: `pydantic-settings` 또는 `os.environ` 활용. `VALKEY_HOST`, `VALKEY_PORT`, `VALKEY_INDEX` 등 로드.
    *   **Clients**: `redis.asyncio.Redis` 클라이언트 인스턴스 생성 및 관리 (Singleton 패턴 권장).

### 3.2 Demo API 구현 (Demo API)
*   **Task ID**: DEMO-002
*   **Files**: `app/demo_api/main.py`, `app/demo_api/search_valkey.py`, `app/demo_api/hybrid.py`, `app/demo_api/schemas.py`
*   **Implementation Details**:
    1.  **Schemas**:
        *   `SearchRequest`: `query`, `top_k`, `mode` (semantic/keyword/hybrid), `weights` (hybrid용).
        *   `SearchResult`: `rank`, `doc_id`, `snippet`, `scores` (dict).
    2.  **Search Logic (`search_valkey.py`)**:
        *   **Semantic**: `FT.SEARCH` with `KNN`. Query vector 생성은 `common.py`의 `embed_text_ollama` 재사용(또는 `httpx`로 직접 호출).
        *   **Keyword**: `FT.SEARCH` with text query (BM25).
    3.  **Hybrid Logic (`hybrid.py`)**:
        *   Keyword Top-K + Vector Top-K 결과 Fetch.
        *   `doc_id` 기준 Union.
        *   **Normalization**: Min-Max Scaling (각 점수 범위를 0~1로 변환).
        *   **Weighted Sum**: `score = w_k * norm_bm25 + w_v * norm_vector`.
        *   Re-sort & Top-K Slice.
    4.  **Endpoints**: `/search/semantic`, `/search/keyword`, `/search/hybrid`.

### 3.3 Streamlit UI 구현 (Streamlit UI)
*   **Task ID**: DEMO-003
*   **Files**: `app/streamlit_app/app.py`, `app/streamlit_app/ui_presets.py`, `app/streamlit_app/api_client.py`
*   **Implementation Details**:
    1.  **Layout**:
        *   **Sidebar**: Mode(Radio), Top-K(Selectbox), Hybrid Weights(Slider), Debug(Checkbox).
        *   **Main**: Query Input(Text Input), Preset Buttons(Grid), Results(Container).
    2.  **Preset Buttons**: `ui_presets.py`에 정의된 9개 쿼리(Semantic 3, Keyword 3, Hybrid 3)를 버튼으로 렌더링. 클릭 시 Session State의 Query 업데이트 및 검색 트리거.
    3.  **Result Display**:
        *   `st.markdown` 또는 `st.dataframe` 활용.
        *   Debug Mode ON일 경우 `st.json` 또는 `st.expander`로 `scores` 상세 정보 표시.
    4.  **API Client**: `httpx`를 사용하여 FastAPI 백엔드 호출.

### 3.4 문서화 (Documentation)
*   **Task ID**: DEMO-004
*   **File**: `README.md`, `docs/manual_test_sprint4_guide.md`
*   **Implementation Details**:
    *   **README.md**: Demo App 실행을 위한 간략한 명령어 추가.
    *   **manual_test_sprint4_guide.md**:
        *   **Execution**: 단계별 상세 실행 가이드 (Deps 설치 -> API 실행 -> UI 실행).
        *   **Demo Scenario**: 각 검색 모드별 강점을 보여주는 예시 시나리오 및 예상 결과 기술.

### 3.5 검색 결과 표시 개선 (Search Result Enhancement)
*   **Task ID**: DEMO-005
*   **Files**: `app/demo_api/schemas.py`, `app/demo_api/search_valkey.py`, `app/streamlit_app/app.py`
*   **Implementation Details**:
    1.  **Schema Update**:
        *   `SearchResult` 스키마에 `content` 필드 추가 (Optional).
    2.  **Search Logic Update**:
        *   Valkey 검색 시 반환된 문서의 본문(`content` 또는 `text` 필드)을 `SearchResult`에 매핑.
    3.  **UI Update**:
        *   Streamlit 결과 표시 영역에 `snippet` 대신 또는 함께 원본 `content`를 확장 가능한 형태(`st.expander`)나 텍스트 영역으로 표시.
        *   사용자가 검색 결과의 문맥을 더 잘 파악할 수 있도록 UI 개선.

### 3.6 Backend - Schema Update (Schema)
*   **Task ID**: DEMO-006
*   **Files**: `postgres/01_schema.sql`
*   **Implementation Details**:
    *   **Table**: `chunk_embeddings`
    *   **Columns**: `chunk_id` (PK), `doc_id`, `embedding` (VECTOR(768)), `model_name`, `model_version`, `text_hash`, `embedded_at`.

### 3.7 Backend - Indexer Update (Indexer)
*   **Task ID**: DEMO-007
*   **Files**: `app/indexer.py`
*   **Implementation Details**:
    *   **CHUNK_UPSERT**:
        1.  Postgres `chunk_embeddings`에 UPSERT.
        2.  Valkey에 HSET (기존 로직).
    *   **CHUNK_DELETE**:
        1.  Postgres `chunk_embeddings`에서 삭제.
        2.  Valkey에서 삭제 (기존 로직).

### 3.8 Backend - Rebuild Tool (Rebuild)
*   **Task ID**: DEMO-008
*   **Files**: `app/tools/rebuild_valkey_from_pg.py`
*   **Implementation Details**:
    *   **Logic**:
        1.  Postgres `chunk_embeddings` 조회 (Batch).
        2.  Valkey 인덱스 초기화 (Optional).
        3.  Valkey에 데이터 재적재 (Pipeline 활용).

### 3.9 Demo API - Engine Support (API Engine)
*   **Task ID**: DEMO-009
*   **Files**: `app/demo_api/schemas.py`, `app/demo_api/search_valkey.py`
*   **Implementation Details**:
    *   **Schema**: `SearchRequest`에 `engine` 필드 추가 (enum: `valkey`, `pgvector`, `fallback`).
    *   **Logic**:
        *   `valkey`: 기존 로직.
        *   `pgvector`: `pgvector` 쿼리 실행.
        *   `fallback`: `valkey` 실패 시 `pgvector` 실행.

### 3.10 Streamlit UI - Engine Selector (UI Engine)
*   **Task ID**: DEMO-010
*   **Files**: `app/streamlit_app/app.py`
*   **Implementation Details**:
    *   **Sidebar**: 'Search Engine' 라디오 버튼 또는 셀렉트박스 추가.
    *   **Debug**: 결과 화면에 실제 사용된 엔진 정보 표시.

## 4. 검증 계획 (Verification Plan)
*   **Prerequisite**: `source .venv/bin/activate` (기존 venv 활용)
*   **Step 1**: `pip install -r requirements-demo.txt` 설치 확인.
*   **Step 2**: API 서버 구동 (`uvicorn`) 및 Swagger UI (`/docs`) 접속 확인.
*   **Step 3**: Streamlit 앱 구동 및 브라우저 접속 확인.
*   **Step 4**: Preset 버튼 클릭하여 각 모드별 검색 결과 정상 출력 확인.
*   **Step 5**: Debug 모드에서 점수 Breakdown 표시 확인.
