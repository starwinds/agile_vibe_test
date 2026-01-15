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
