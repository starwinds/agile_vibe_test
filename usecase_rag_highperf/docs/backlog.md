# Product Backlog: RAG High-Perf System

본 문서는 `prd.md`를 기반으로 도출된 개발 요구사항(Backlog)을 정의합니다.

## Epic 1: 인프라 및 환경 구성 (Infrastructure)
기반이 되는 Docker 환경과 데이터베이스 서비스를 구축합니다.

- [x] **INFRA-001: Docker Compose 구성**
    - `docker-compose.yml` 작성
    - Postgres 16.9 (`pgvector/pgvector:pg16`) 컨테이너 설정 (Port: 5432)
    - Valkey (`valkey/valkey-bundle:latest`) 컨테이너 설정 (Port: 6379)
    - 각 서비스 Healthcheck 설정
    - 데이터 영속성을 위한 Volume 설정 (`pgdata`, `vkdata`)

- [x] **INFRA-002: 환경 변수 설정**
    - `.env.example` 파일 작성
    - Postgres 접속 정보 (User, Password, DB, Port, DSN) 정의
    - Valkey 접속 정보 (Host, Port, Password) 정의

- [x] **INFRA-003: Ollama 환경 변수 추가**
    - `.env.example`에 `OLLAMA_BASE_URL` (기본값: `http://localhost:11434`), `OLLAMA_MODEL` (기본값: `nomic-embed-text`) 추가

## Epic 2: 데이터베이스 모델링 (Database)
Postgres 스키마와 초기 데이터를 구성합니다.

- [x] **DB-001: 확장 및 스키마 스크립트 작성**
    - `postgres/00_extensions.sql`: `vector` extension 활성화
    - `postgres/01_schema.sql`: 테이블 생성
        - `documents`: 문서 메타데이터
        - `chunks`: 청크 텍스트 및 해시
        - `doc_acl`: 문서 접근 권한
        - `outbox_events`: Transactional Outbox 패턴용 이벤트 테이블 (인덱스 포함)

- [x] **DB-002: 초기 데이터 시드 (Optional)**
    - `postgres/02_seed.sql`: 필요 시 초기 데이터 구성 (현재는 빈 파일)

## Epic 3: 애플리케이션 개발 (Application)
Python 기반의 RAG 파이프라인 애플리케이션을 개발합니다.

- [x] **APP-001: 공통 모듈 및 의존성 관리**
    - `app/requirements.txt`: `psycopg`, `redis`, `numpy` 등 의존성 명시
    - `app/common.py`:
        - 임베딩 차원 상수 정의 (384 dim)
        - Stub 임베딩 생성 함수 (`embed_text_stub`) 구현
        - Numpy 배열 바이너리 패킹 함수 (`pack_f32`) 구현

- [x] **APP-002: Ingest 서비스 구현**
    - `app/ingest.py`:
        - 텍스트 청킹 로직 구현 (Overlap 지원)
        - Postgres 트랜잭션 처리:
            - `documents`, `chunks` Upsert
            - `doc_acl` 갱신
            - `outbox_events` 발행 (`CHUNK_UPSERT`)

- [x] **APP-003: Indexer 서비스 구현**
    - `app/indexer.py`:
        - Valkey 연결 및 인덱스(`idx:chunks`) 생성 체크/생성 (`FT.CREATE`)
        - Postgres `outbox_events` 폴링 루프 구현
        - 이벤트 처리:
            - `CHUNK_UPSERT`: 임베딩 생성 후 Valkey `HSET`
            - `CHUNK_DELETE`: Valkey 키 삭제
        - 이벤트 처리 완료 마킹 (`processed_at` 업데이트)

- [x] **APP-004: Query 서비스 구현**
    - `app/query.py`:
        - 사용자 쿼리 임베딩 생성
        - Valkey `FT.SEARCH` 실행 (KNN 검색, Hybrid 필터링)
        - 검색된 `doc_id` 기반 Postgres `doc_acl` 권한 검증
        - 권한 있는 청크 본문 조회 및 컨텍스트 조합

- [x] **APP-005: Healthcheck 스크립트**
    - `app/healthcheck.py`: Postgres, Valkey, Index 상태 점검 로직

- [x] **APP-006: Ollama 임베딩 연동**
    - `app/requirements.txt`: `requests` 라이브러리 추가
    - `app/common.py` 수정:
        - `EMBED_DIM`을 768로 변경
        - `embed_text_stub`를 `embed_text_ollama`로 변경 및 실제 API 호출 구현

## Epic 4: 검증 및 문서화 (Verification)
구현된 시스템의 동작을 검증하고 사용법을 문서화합니다.

- [x] **VER-001: End-to-End 테스트 수행**
    - 컨테이너 구동 확인
    - Ingest 실행 및 DB 적재 확인
    - Indexer 실행 및 Valkey 색인 확인
    - Query 실행 및 결과(ACL 적용됨) 확인

- [x] **VER-002: README 작성**
    - 프로젝트 설치 및 실행 가이드 (`docker compose`, `venv`, 실행 명령어)
    - 트러블슈팅 가이드

## Epic 5: 고도화 요구사항 (Advanced Requirements)
Single Tenant 환경에서의 대규모 데이터 처리 및 성능 벤치마크를 위한 도구를 개발합니다.

- [ ] **ADV-001: 데이터 생성기 개발 (Data Generator)**
    - `app/generate_dataset.py` 구현
    - Single Tenant(`t1`) 환경을 가정한 대규모 코퍼스 생성
    - CLI 인자 지원: `--docs`, `--avg-chunks`, `--update-rate`, `--delete-rate`, `--seed`
    - Postgres 테이블(`documents`, `chunks`, `doc_acl`, `outbox_events`)에 데이터 적재
    - `data/manifest.json` 생성

- [ ] **ADV-002: 질의 생성기 개발 (Query Generator)**
    - `app/generate_queries.py` 구현
    - 벤치마크용 질의 세트 생성
    - CLI 인자 지원: `--queries`, `--mix` (semantic, keyword, hybrid, freshness 비율), `--seed`
    - Golden Answer(기대되는 `doc_id` 목록) 포함
    - `data/queries.jsonl` 파일 생성

- [ ] **ADV-003: 벤치마크 도구 개발 (Benchmark Tool)**
    - `app/bench.py` 및 `app/metrics.py` 구현
    - Mode A (`valkey_knn`): Valkey 검색 성능 측정
    - Mode B (`hybrid_fetch`): Valkey 검색 + Postgres 본문 조회 E2E 성능 측정
    - CLI 인자 지원: `--queries`, `--mode`, `--k`, `--concurrency`, `--duration-sec`, `--report`
    - `metrics.py`: Latency(p50, p95, p99), QPS, Error Rate 계산

- [ ] **ADV-004: 문서화 업데이트**
    - `README.md` 업데이트
    - 새로운 스크립트(`generate_dataset.py`, `generate_queries.py`, `bench.py`) 사용법 추가
    - 벤치마크 실행 및 결과 해석 가이드 추가

## Epic 6: Demo App 개발 (Demo Application)
End-user가 체감할 수 있는 검색 데모 애플리케이션(FastAPI + Streamlit)을 개발합니다.

- [x] **DEMO-001: Demo API 프로젝트 구조 및 의존성 구성**
    - `app/demo_api/` 디렉토리 및 기본 파일(`main.py`, `settings.py`, `clients.py`) 생성
    - `app/streamlit_app/` 디렉토리 생성
    - `requirements-demo.txt` 작성 (`fastapi`, `uvicorn`, `streamlit`, `httpx` 등)

- [x] **DEMO-002: Demo API 구현 (Search Logic)**
    - `app/demo_api/search_valkey.py`: Semantic(Vector), Keyword(BM25/ILIKE) 검색 구현
    - `app/demo_api/hybrid.py`: Hybrid 검색 (2-pass union + rerank) 구현
    - `app/demo_api/main.py`: `/search/semantic`, `/search/keyword`, `/search/hybrid` 엔드포인트 구현

- [x] **DEMO-003: Streamlit UI 구현 (Search Playground)**
    - `app/streamlit_app/app.py`: 검색 모드 선택, Top-K 설정, Hybrid 가중치 조절 UI 구현
    - 검색 결과 리스트 및 Debug 모드(점수 Breakdown) 표시 구현
    - `app/streamlit_app/ui_presets.py`: 데모용 프리셋 쿼리 9종 버튼 연동

- [x] **DEMO-004: 문서화 및 가이드**
    - `README.md`에 Demo App 실행 방법 및 시나리오 추가

- [x] **DEMO-005: 검색 결과 표시 개선 (Search Result Enhancement)**
    - 검색 결과에 Vector Score, Distance 외에 사용자가 인식할 수 있는 원본 콘텐츠(본문 텍스트 등)를 함께 표시
    - 필요 시 `SearchResult` 스키마 및 UI 레이아웃 조정

## Epic 7: Pattern B Incremental (Postgres SoR)
기존 Pattern A(Valkey-centric) 구조 위에 Postgres를 Embedding SoR로 도입하여 안정성을 강화하고, Engine 선택 기능을 추가합니다.

- [x] **DEMO-006: Backend - Schema Update**
    - `postgres/01_schema.sql`: `chunk_embeddings` 테이블 추가
    - Columns: `chunk_id`, `doc_id`, `embedding`, `model_name`, `model_version`, `text_hash`, `embedded_at`

- [x] **DEMO-007: Backend - Indexer Update**
    - `app/indexer.py` 수정
    - `CHUNK_UPSERT`: Postgres `chunk_embeddings`에 UPSERT 후 Valkey HSET
    - `CHUNK_DELETE`: Postgres `chunk_embeddings` 삭제 후 Valkey DEL

- [x] **DEMO-008: Backend - Rebuild Tool**
    - `app/tools/rebuild_valkey_from_pg.py` 구현
    - Postgres `chunk_embeddings` 조회 -> Valkey 인덱스 초기화 -> 재적재 (Pipeline)

- [x] **DEMO-009: Demo API - Engine Support**
    - `app/demo_api/` 수정
    - `SearchRequest`에 `engine` 파라미터 추가 (`valkey`, `pgvector`, `fallback`)
    - `search_valkey.py`에 `pgvector` 검색 로직 및 Fallback 로직 추가

- [x] **DEMO-010: Streamlit UI - Engine Selector**
    - `app/streamlit_app/app.py` 수정
    - Sidebar에 Engine 선택(Radio/Select) 추가
    - Debug 모드 시 실제 사용된 Engine 정보 표시

## Epic 8: 검색 고도화 및 최적화 (Advanced Search & Optimization)
Valkey의 한계를 극복하고 Postgres의 강력한 검색 기능을 활용하여 검색 품질과 성능을 최적화합니다.

- [ ] **ADV-005: Postgres Full-Text Search 도입**
    - `chunks` 테이블에 `tsvector` 컬럼 추가 및 `GIN` 인덱스 생성
    - `pg_trgm` 확장 활성화 및 `chunk_text`에 인덱스 생성
    - `demo_api`의 Keyword 검색 로직을 `ILIKE`에서 `websearch_to_tsquery` 또는 `plainto_tsquery`로 고도화 (Rank 지원)

- [ ] **ADV-006: Hybrid Search 2.0 (RRF)**
    - 현재의 선형 가중치 합(Linear Weighted Sum) 방식 외에 RRF(Reciprocal Rank Fusion) 알고리즘 도입
    - 점수 스케일이 다른 Vector(Cosine Sim)와 Keyword(TS Rank) 결과를 효과적으로 결합

- [ ] **ADV-007: Metadata Filtering**
    - `SearchRequest`에 `filter` 파라미터 추가 (e.g., `tenant_id`, `doc_id`, `created_at` 범위)
    - Valkey `FT.SEARCH` 및 Postgres 쿼리에 필터 조건 동적 적용 구현

## Epic 9: 고품질 샘플 데이터 생성 (High-Quality Data Generation)
의미 없는 무작위 텍스트 대신 실제 문맥을 가진 데이터를 활용하여 RAG 시스템의 신뢰도를 높입니다.

- [ ] **ADV-008: HuggingFace Datasets 연동**
    - `requirements.txt`에 `datasets` 라이브러리 추가
    - `app/generate_dataset.py`에서 외부 데이터셋(e.g., Wikipedia, AG News) 로드 기능 구현

- [ ] **ADV-009: 데이터 샘플링 및 전처리 로직 구현**
    - 로드된 데이터셋에서 지정된 개수만큼의 실제 문서를 추출하는 로직 구현
    - 너무 짧거나 긴 문서 필터링 및 클리닝 전처리 추가

- [ ] **ADV-010: 데이터 생성기 고도화**
    - `Faker.paragraph()`를 실제 데이터셋의 텍스트로 대체
    - 문서 제목(Title) 또한 데이터셋의 메타데이터를 활용하도록 수정

- [ ] **ADV-011: 데이터 품질 검증**
    - 생성된 데이터가 실제 문맥을 유지하는지 확인
    - 대량 데이터 생성 시의 성능(속도) 및 메모리 사용량 최적화


## Epic 10: 다국어 데이터 지원 (Multilingual Data Support)
글로벌 서비스 확장을 대비하여 한국어 등 다국어 데이터 생성 및 검색을 지원합니다.

- [ ] **ADV-012: 한국어 데이터 생성 지원**
    - `app/generate_dataset.py`에 `--language` 인자 추가
    - `ko` 선택 시 `beomi/kowiki-20240401` 데이터셋 로드
    - Fallback으로 `Faker("ko_KR")` 적용
