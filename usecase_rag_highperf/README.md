# RAG High-Perf MVP (Postgres + Valkey)

이 프로젝트는 Postgres(Source of Record)와 Valkey(Vector Search)를 연동한 고성능 RAG 시스템의 MVP 구현체입니다. Transactional Outbox 패턴을 사용하여 데이터 정합성을 보장하며, ACL(Access Control List)을 통한 권한 기반 검색을 지원합니다.

## 1. 시스템 아키텍처
1.  **Ingest**: Postgres에 문서, 청크, ACL 정보를 저장하고 `outbox_events`를 생성합니다.
2.  **Indexer**: Outbox 이벤트를 폴링하여 텍스트 임베딩을 생성하고 Valkey에 벡터 색인을 수행합니다.
3.  **Query**: Valkey에서 KNN 검색을 수행한 후, Postgres의 ACL 정보를 참조하여 최종 결과를 필터링합니다.

## 2. 사전 준비
*   Docker & Docker Compose
*   Python 3.10+
*   Ollama (Local) - `nomic-embed-text` 모델 필요 (`ollama pull nomic-embed-text`)

## 3. 시작하기

### 3.1 환경 설정
```bash
cd usecase_rag_highperf
cp .env.example .env
# .env 파일 내의 접속 정보 확인 및 수정
# OLLAMA_BASE_URL (기본: http://localhost:11434) 설정
```

### 3.2 인프라 구동
```bash
docker compose up -d
```

### 3.3 의존성 설치
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
```

## 4. 실행 순서

### 4.1 상태 점검
```bash
python app/healthcheck.py
```

### 4.2 데이터 적재 (Ingest)
```bash
python app/ingest.py
```

### 4.3 색인 (Indexer)
이 프로세스는 계속 실행되어 이벤트를 처리합니다.
```bash
python app/indexer.py
```

### 4.4 검색 (Query)
```bash
python app/query.py
```

### 3.4 Ollama 상태 점검
최근 업데이트된 `app/check_ollama.py` 스크립트를 통해 Ollama 서비스와 `nomic-embed-text` 모델 존재 여부를 확인할 수 있습니다.
```bash
python app/check_ollama.py
```

## 5. 프로젝트 구조
*   `app/`: Python 애플리케이션 소스 코드
    *   `check_ollama.py`: Ollama 연동 확인 유틸리티
*   `docs/`: 문서 및 분석 결과
    *   `retro2.md`: Sprint 2(Ollama 연동) 회고록
*   `postgres/`: DB 스키마 및 초기화 스크립트
*   `docker-compose.yml`: 인프라 설정 파일

## 6. 성능 벤치마크 (Sprint 3)

대규모 데이터 생성 및 성능 측정을 위한 도구 모음입니다.

### 6.1 데이터 생성
대량의 문서 및 Outbox 이벤트를 생성합니다.
```bash
python app/generate_dataset.py --docs 1000 --avg-chunks 10 --update-rate 0.1
```

### 6.2 질의 생성
벤치마크에 사용할 질의 데이터를 생성합니다. (Semantic, Keyword, Freshness 등 다양한 유형)
```bash
python app/generate_queries.py --queries 100
```

### 6.3 벤치마크 실행
생성된 질의를 사용하여 검색 성능을 측정합니다.
*   **Vector Search Only (Mock Embedding)**:
    ```bash
    python app/bench.py --mode valkey_knn --mock-embedding --concurrency 50
    ```
*   **Hybrid Search (Real Embedding + Fetch)**:
    ```bash
    python app/bench.py --mode hybrid_fetch --no-mock-embedding
    ```

### 6.4 결과 확인
벤치마크 결과는 `out/` 디렉토리에 JSON 파일로 저장됩니다.

## 7. Demo App (Sprint 4)

FastAPI 백엔드와 Streamlit 프론트엔드로 구성된 하이브리드 검색 데모입니다.

### 7.1 설치
```bash
pip install -r requirements-demo.txt
```

### 7.2 API 실행 (Backend)
프로젝트 루트(`agile_vibe_test`)에서 실행해야 합니다:
```bash
uvicorn usecase_rag_highperf.app.demo_api.main:app --reload --port 8000
```
Swagger UI: http://localhost:8000/docs

### 7.3 Streamlit 실행 (Frontend)
새 터미널에서 실행:
```bash
cd usecase_rag_highperf/app/streamlit_app
streamlit run app.py
```
브라우저 접속: http://localhost:8501
