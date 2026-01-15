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

## 4. 검증 계획 (Verification Plan)
*   **Prerequisite**: `source .venv/bin/activate` (기존 venv 활용)
*   **Step 1**: `pip install -r requirements-demo.txt` 설치 확인.
*   **Step 2**: API 서버 구동 (`uvicorn`) 및 Swagger UI (`/docs`) 접속 확인.
*   **Step 3**: Streamlit 앱 구동 및 브라우저 접속 확인.
*   **Step 4**: Preset 버튼 클릭하여 각 모드별 검색 결과 정상 출력 확인.
*   **Step 5**: Debug 모드에서 점수 Breakdown 표시 확인.
