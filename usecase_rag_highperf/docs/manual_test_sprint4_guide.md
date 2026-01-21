# Sprint 4 Manual Test Guide: Demo App & Pattern B

이 문서는 Sprint 4에서 개발된 **Hybrid Search Demo App**과 **Pattern B (Postgres SoR)** 기능을 사용자가 직접 테스트하는 방법을 안내합니다.

## 1. 개요 (Overview)
*   **목표**: 
    1. Semantic, Keyword, Hybrid 검색을 시각적으로 체험하고 비교합니다.
    2. Postgres를 SoR로 활용하여 Valkey 장애 시 복구 및 Fallback 검색을 검증합니다.
*   **구성 요소**:
    *   **Demo API**: Valkey 및 PGVector 기반 검색 엔드포인트 제공.
    *   **Streamlit UI**: 검색 엔진 선택 및 결과 시각화.
    *   **Rebuild Tool**: Postgres 데이터를 이용한 Valkey 인덱스 복구 도구.

## 2. 사전 준비 (Prerequisites)
*   **인프라 구동**: `docker compose up -d` (Postgres, Valkey 실행 중이어야 함).
*   **데이터 적재**: Valkey에 인덱스와 데이터가 있어야 합니다.
    *   Sprint 3의 `generate_dataset.py` 및 `indexer.py`를 실행하여 데이터를 채우는 것을 권장합니다.
    *   **Pattern B 검증을 위해 반드시 Indexer를 실행해야 Postgres `chunk_embeddings`에도 데이터가 적재됩니다.**
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
# 패키지 경로 인식을 위해 프로젝트 루트(agile_vibe_test)로 이동하여 실행합니다.
cd ..
uvicorn usecase_rag_highperf.app.demo_api.main:app --host 0.0.0.0 --port 8000
```
*   시작 로그에 `Ollama is connected.`가 표시되는지 확인합니다.

### Step 3: Frontend UI 실행
터미널 2 (새 탭/창):
```bash
# 프로젝트 루트 또는 usecase_rag_highperf 디렉토리에서 실행
cd usecase_rag_highperf
source .venv/bin/activate
cd app/streamlit_app
streamlit run app.py
```
*   브라우저가 자동으로 열리거나 `http://localhost:8501`로 접속합니다.

## 4. 테스트 시나리오 (Test Scenarios)

### Scenario A: Backend Health Check
1.  Streamlit 사이드바에서 **"Check Backend Health"** 버튼을 클릭합니다.
2.  **"Connected! Ollama: connected"** 메시지가 표시되는지 확인합니다.

### Scenario B: Semantic Search (Valkey)
1.  사이드바 **Search Mode**를 `semantic`으로 선택합니다.
2.  **Search Engine**을 `valkey`로 선택합니다.
3.  **Presets**에서 "Semantic 1" 버튼을 클릭합니다.
4.  검색 결과가 표시되며, **Debug Mode** 체크박스를 켜면 `Source: valkey`가 표시되는지 확인합니다.
5.  각 결과 카드의 `View Content`를 확장하여 문서의 본문이 정상적으로 조회되는지 확인합니다.

### Scenario C: Pattern B - PGVector Search & Fallback
1.  **PGVector 직접 검색**:
    *   **Search Engine**을 `pgvector`로 선택합니다.
    *   검색 실행 후 결과가 Valkey와 유사하게 나오는지 확인합니다.
    *   Debug 모드에서 `Source: pgvector` 확인.
2.  **Fallback 테스트**:
    *   (고급) `docker stop` 등으로 Valkey 컨테이너를 중지시키거나, 코드상에서 Valkey 포트를 임의로 변경하여 연결 오류를 유도합니다.
    *   **Search Engine**을 `fallback`으로 선택합니다.
    *   검색 실행 시 에러 없이 결과가 반환되는지 확인합니다 (내부적으로 PGVector 사용).
    *   Debug 모드에서 `Source: pgvector`가 표시되어야 합니다.

### Scenario D: Pattern B - Disaster Recovery (Rebuild)
Valkey 데이터가 유실되었을 때 Postgres SoR을 통해 복구하는 시나리오입니다.

1.  **Valkey 데이터 삭제**:
    ```bash
    # redis-cli 또는 valkey-cli 접속
    valkey-cli FLUSHALL
    ```
2.  **검색 실패 확인**:
    *   Streamlit에서 `valkey` 엔진으로 검색 시 결과가 0건이어야 합니다.
3.  **Rebuild Tool 실행**:
    ```bash
    python app/tools/rebuild_valkey_from_pg.py
    ```
    *   "Fetching data from Postgres SoR..." 및 "Rebuild complete" 로그 확인.
4.  **복구 확인**:
    *   Streamlit에서 다시 `valkey` 엔진으로 검색하여 결과가 정상적으로 나오는지 확인합니다.

### Scenario E: Hybrid Search
1.  사이드바 **Search Mode**를 `hybrid`로 선택합니다.
2.  **Hybrid Weights** 슬라이더를 조절해 봅니다 (예: Semantic 0.8 / Keyword 0.2).
3.  검색을 실행하고 결과의 순위가 변경되는지 관찰합니다.
    *   Debug Mode 체크박스를 켜면 각 결과의 `vector` 점수와 `bm25` 점수, 최종 `final` 점수를 상세히 볼 수 있습니다.

### Scenario F: Multi-language Data Generation (Korean Support)
`ADV-012` 과제에서 구현된 한국어 데이터 생성 및 적재 기능을 테스트합니다.

1.  **한국어 데이터 생성**:
    ```bash
    # --language ko 옵션을 사용하여 한국어 위키백과 기반 데이터 생성
    python app/generate_dataset.py --docs 50 --language ko
    ```
    *   `wikimedia/wikipedia` (ko) 데이터셋을 자동으로 로드하며, 실패 시 한국어 로케일이 적용된 `Faker`를 사용합니다.
2.  **데이터 인덱싱**:
    ```bash
    # 생성된 outbox_events를 처리하여 Postgres SoR 및 Valkey에 적재
    python app/indexer.py
    ```
3.  **한국어 검색 테스트**:
    *   Streamlit UI에 접속합니다.
    *   **Search Mode**를 `semantic`으로 설정합니다.
    *   검색창에 한국어 쿼리(예: "대한민국의 역사", "서울의 고층 빌딩")를 입력하고 검색 결과가 한국어로 정상 출력되는지 확인합니다.

## 5. 문제 해결 (Troubleshooting)

*   **API Connection Error**: Backend API가 실행 중인지 (`localhost:8000`) 확인하세요.
*   **Ollama Disconnected**: Ollama가 실행 중인지 확인하고, `.env`의 `OLLAMA_BASE_URL`이 올바른지 확인하세요.
*   **No Results**: 데이터가 인덱싱되었는지 확인하세요. `valkey-cli`로 `FT.INFO idx:chunks`를 조회하거나 `app/indexer.py` 로그를 확인하세요.
*   **Rebuild 0 chunks**: `app/indexer.py`가 실행된 적이 없어서 Postgres `chunk_embeddings` 테이블이 비어있을 수 있습니다. `app/indexer.py`를 실행하여 이벤트를 처리하세요.
