# Sprint 4 Manual Test Guide: Demo App (FastAPI + Streamlit)

이 문서는 Sprint 4에서 개발된 **Hybrid Search Demo App**을 사용자가 직접 테스트하는 방법을 안내합니다.

## 1. 개요 (Overview)
*   **목표**: Semantic, Keyword, Hybrid 검색을 시각적으로 체험하고 비교합니다.
*   **구성 요소**:
    *   **Demo API**: Valkey 기반 검색 엔드포인트 제공.
    *   **Streamlit UI**: 사용자 친화적인 검색 인터페이스 제공.

## 2. 사전 준비 (Prerequisites)
*   **인프라 구동**: `docker compose up -d` (Postgres, Valkey 실행 중이어야 함).
*   **데이터 적재**: Valkey에 인덱스와 데이터가 있어야 합니다.
    *   Sprint 3의 `generate_dataset.py` 및 `indexer.py`를 실행하여 데이터를 채우는 것을 권장합니다.
    *   예: `python app/generate_dataset.py --docs 100` -> `python app/indexer.py` (잠시 대기).
*   **Ollama 실행**: Semantic 검색을 위해 로컬 Ollama (`nomic-embed-text`)가 실행 중이어야 합니다.

## 3. 실행 절차 (Execution Steps)

### Step 1: 의존성 설치
```bash
cd usecase_rag_highperf
source .venv/bin/activate
pip install -r requirements-demo.txt
```

### Step 2: Backend API 실행
터미널 1:
```bash
uvicorn usecase_rag_highperf.app.demo_api.main:app --host 0.0.0.0 --port 8000
```
*   시작 로그에 `Ollama is connected.`가 표시되는지 확인합니다.

### Step 3: Frontend UI 실행
터미널 2:
```bash
cd usecase_rag_highperf/app/streamlit_app
streamlit run app.py
```
*   브라우저가 자동으로 열리거나 `http://localhost:8501`로 접속합니다.

## 4. 테스트 시나리오 (Test Scenarios)

### Scenario A: Backend Health Check
1.  Streamlit 사이드바에서 **"Check Backend Health"** 버튼을 클릭합니다.
2.  **"Connected! Ollama: connected"** 메시지가 표시되는지 확인합니다.

### Scenario B: Semantic Search
1.  사이드바 **Search Mode**를 `semantic`으로 선택합니다.
2.  **Presets**에서 "Semantic 1" 버튼을 클릭합니다.
3.  검색 결과가 표시되며, `Score` (Similarity)가 높은 순으로 정렬되는지 확인합니다.
4.  결과 스니펫이 질문과 의미적으로 유사한지 확인합니다.

### Scenario C: Keyword Search
1.  사이드바 **Search Mode**를 `keyword`로 선택합니다.
2.  **Presets**에서 "Keyword 1" (e.g., ERROR_503) 버튼을 클릭합니다.
3.  해당 키워드가 포함된 문서가 상위에 노출되는지 확인합니다.

### Scenario D: Hybrid Search
1.  사이드바 **Search Mode**를 `hybrid`로 선택합니다.
2.  **Hybrid Weights** 슬라이더를 조절해 봅니다 (예: Semantic 0.8 / Keyword 0.2).
3.  검색을 실행하고 결과의 순위가 변경되는지 관찰합니다.
    *   **Debug Mode** 체크박스를 켜면 각 결과의 `vector` 점수와 `bm25` 점수, 최종 `final` 점수를 상세히 볼 수 있습니다.

## 5. 문제 해결 (Troubleshooting)

*   **API Connection Error**: Backend API가 실행 중인지 (`localhost:8000`) 확인하세요.
*   **Ollama Disconnected**: Ollama가 실행 중인지 확인하고, `.env`의 `OLLAMA_BASE_URL`이 올바른지 확인하세요.
*   **No Results**: 데이터가 인덱싱되었는지 확인하세요. `valkey-cli`로 `FT.INFO idx:chunks`를 조회하거나 `app/indexer.py` 로그를 확인하세요.