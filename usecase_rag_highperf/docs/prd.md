# Product Requirements Document (PRD): RAG High-Perf (Postgres + Valkey)

## 1. 개요
본 문서는 WSL2 Ubuntu 환경에서 Postgres(SoR)와 Valkey(Vector Search)를 활용한 고성능 RAG(Retrieval-Augmented Generation) 시스템의 샘플 구현을 위한 요구사항을 정의합니다.

## 2. 목표
1.  **인프라 구성**: Docker Compose를 사용하여 다음 서비스를 구동합니다.
    *   **Postgres**: `pgvector/pgvector:pg16` (PostgreSQL 16.9, Vector extension 포함)
    *   **Valkey**: `valkey/valkey-bundle:latest` (VectorSearch 및 FT.* 명령어 지원)
2.  **End-to-End 플로우 검증**: Python 애플리케이션을 통해 다음 과정을 검증합니다.
    *   **Ingest**: 문서/청크/ACL 데이터 저장 및 Outbox 이벤트 생성 (Postgres SoR)
    *   **Indexer**: Outbox 이벤트를 소비하여 임베딩 생성(Stub) 및 Valkey 색인
    *   **Query**: Valkey KNN 검색(TopK) 후 Postgres에서 ACL 확인 및 본문 조회

## 3. 프로젝트 구조
루트 디렉토리명은 `usecase_rag_highperf`로 설정하며, 다음과 같은 구조를 준수해야 합니다.

```text
usecase_rag_highperf/
  README.md
  .env.example
  docker-compose.yml

  postgres/
    00_extensions.sql
    01_schema.sql
    02_seed.sql

  app/
    requirements.txt
    common.py
    ingest.py
    indexer.py
    query.py
    healthcheck.py
```

## 4. 상세 요구사항

### 4.1 인프라 설정 (`docker-compose.yml`)
*   **Postgres Service**:
    *   이미지: `pgvector/pgvector:pg16`
    *   포트: 5432
    *   초기화 스크립트: `postgres/` 디렉토리의 SQL 파일 마운트
    *   Healthcheck: `pg_isready` 사용
*   **Valkey Service**:
    *   이미지: `valkey/valkey-bundle:latest`
    *   포트: 6379
    *   Healthcheck: `valkey-cli PING` 사용

### 4.2 환경 변수 (`.env`)
*   Postgres 접속 정보 (User, Password, DB, Port, DSN)
*   Valkey 접속 정보 (Host, Port, Password)
*   **Ollama 설정**: `OLLAMA_BASE_URL` (기본값: `http://localhost:11434`), `OLLAMA_MODEL` (기본값: `nomic-embed-text`)

### 4.3 데이터베이스 스키마 (`postgres/`)
*   **Extensions**: `vector` 확장 설치
*   **Tables**:
    *   `documents`: 문서 메타데이터 (doc_id, tenant_id, title, version 등)
    *   `chunks`: 문서 청크 데이터 (chunk_id, doc_id, chunk_text, chunk_hash 등)
    *   `doc_acl`: 문서 접근 제어 목록 (tenant_id, doc_id, principal, permission)
    *   `outbox_events`: 데이터 변경 이벤트 저장 (Transactional Outbox 패턴 적용)

### 4.4 애플리케이션 로직 (`app/`)
*   **`common.py`**:
    *   임베딩 차원 정의: `768` (nomic-embed-text 기준)
    *   임베딩 생성 함수: `OLLAMA_BASE_URL`의 `/api/embeddings` 엔드포인트를 호출하여 실제 임베딩 생성 (Stub 대체)
    *   바이너리 패킹 함수 제공
*   **`ingest.py`**:
    *   텍스트 청킹 및 해시 생성
    *   Postgres 트랜잭션 내에서 문서, 청크, ACL 저장 및 Outbox 이벤트 생성 (`CHUNK_UPSERT`)
*   **`indexer.py`**:
    *   Valkey 인덱스(`idx:chunks`) 생성 (존재하지 않을 경우)
    *   Postgres `outbox_events` 폴링 및 처리
    *   Valkey에 데이터 색인 (HSET) 또는 삭제
    *   처리 완료된 이벤트 마킹
*   **`query.py`**:
    *   Valkey `FT.SEARCH`를 이용한 KNN 검색
    *   검색 결과에 대해 Postgres `doc_acl` 테이블을 조회하여 권한 검증
    *   권한이 있는 문서의 청크 본문을 조회하여 컨텍스트 조합
*   **`healthcheck.py`**: Postgres 및 Valkey 연결 상태, 인덱스 준비 상태 확인

## 5. 실행 및 검증 시나리오

### 5.1 실행 환경
*   WSL2 Ubuntu 터미널

### 5.2 실행 절차
1.  `.env` 파일 생성 및 설정
2.  `docker compose up -d`로 컨테이너 구동
3.  Python 가상환경 생성 및 의존성 설치 (`requirements.txt`)
4.  `healthcheck.py`로 서비스 상태 확인
5.  `ingest.py` 실행: 데이터 적재 및 이벤트 발행 확인
6.  `indexer.py` 실행: 인덱스 생성 및 데이터 색인 확인
7.  `query.py` 실행: 검색 결과 및 컨텍스트 출력 확인

### 5.3 검증 기준
*   Docker 컨테이너가 정상적으로 실행되고 Healthy 상태여야 함.
*   Ingest 실행 시 DB에 데이터가 정상적으로 적재되어야 함.
*   Indexer 실행 시 Valkey에 인덱스가 생성되고 키가 추가되어야 함.
*   Query 실행 시 검색 결과가 반환되고, ACL이 적용된 본문 텍스트가 출력되어야 함.

## 6. 고도화 요구사항 (Single Tenant Data Query Bench)

기존 `rag-highperf-pg-valkey` 샘플 레포지토리를 확장하여 **High Performance RAG 데모**를 위한 **현실적인 샘플 데이터/쿼리 생성기 + 벤치마크 스크립트**를 추가합니다.

### 6.1 전제 조건
*   **Single tenant만 고려**: tenant_id는 고정값 `t1`으로 설정하며, 멀티테넌시 로직은 제거합니다.
*   **ACL 단순화**: 기본적으로 모든 principal이 접근 가능하며, 선택적으로 일부 문서(5% 내외)에 대해서만 `user:alice` 전용 ACL을 적용합니다.
*   **기존 구조 유지**: Postgres (SoR + outbox), Valkey (VectorSearch serving), indexer(outbox consumer) 구조를 유지합니다.

### 6.2 추가 파일 구조 (`app/`)
기존 파일은 유지하고 다음 파일들을 추가합니다.
*   `generate_dataset.py`: 샘플 문서/청크/업데이트/삭제/outbox 생성
*   `generate_queries.py`: 벤치용 질의 세트 생성 (golden answer 포함)
*   `bench.py`: 성능 벤치 스크립트
*   `metrics.py`: latency(p50/p95/p99), QPS 계산 유틸

### 6.3 샘플 데이터 생성기 (`generate_dataset.py`)
*   **목적**: 검색이 필요해 보이는 규모 있는 corpus 자동 생성 및 문서 변경(업데이트/삭제)을 통한 outbox + indexer 필요성 데모.
*   **CLI 인터페이스**:
    ```bash
    python app/generate_dataset.py --docs 1500 --avg-chunks 12 --update-rate 0.08 --delete-rate 0.02 --seed 42
    ```
*   **생성 데이터 요구사항**:
    *   **문서 도메인 (3종 이상)**: 정책/FAQ, 운영 런북, 기술 문서.
    *   **문서 특성**: 문서마다 고유 키워드 포함, 비슷한 의미지만 표현이 다른 문장 다수 포함.
    *   **업데이트/삭제 이벤트**:
        *   업데이트: `update-rate` 비율, version 증가, 문장 변경, `CHUNK_UPSERT` outbox 이벤트 생성.
        *   삭제: `delete-rate` 비율, status=deleted, `CHUNK_DELETE` outbox 이벤트 생성.
    *   **산출물**: Postgres tables (documents, chunks, doc_acl, outbox_events), `data/manifest.json`.

### 6.4 질의 생성기 (`generate_queries.py`)
*   **목적**: 수백~수천 개 질의 세트 생성 및 질의 유형 혼합을 통한 검색 품질/성능 평가.
*   **CLI 인터페이스**:
    ```bash
    python app/generate_queries.py --queries 800 --mix semantic=0.50 keyword=0.25 hybrid=0.20 freshness=0.05 --seed 42
    ```
*   **질의 유형 요구사항**:
    *   **Semantic (50%)**: 문서 내용을 paraphrase한 자연어 질문.
    *   **Keyword (25%)**: 에러코드/설정값 직접 질의.
    *   **Hybrid (20%)**: 키워드 + 자연어 혼합.
    *   **Freshness (5%)**: 업데이트된 문서의 변경된 내용을 묻는 질문 (기대 결과는 최신 버전).
*   **출력 포맷**: `data/queries.jsonl` (query_id, tenant_id, principal, query_type, query_text, expected_doc_ids 포함).

### 6.5 벤치 스크립트 (`bench.py`)
*   **목적**: High performance RAG 데모를 위한 정량 지표 측정 (p99 latency 중심).
*   **실행 모드**:
    *   **Mode A (`valkey_knn`)**: Valkey VectorSearch만 수행 (순수 retrieval latency).
    *   **Mode B (`hybrid_fetch`)**: Valkey Top-K 검색 + Postgres chunk_text fetch (end-to-end latency).
*   **CLI 인터페이스**:
    ```bash
    python app/bench.py --queries data/queries.jsonl --mode hybrid_fetch --k 40 --concurrency 32 --duration-sec 60 --timeout-ms 200 --report out/bench_hybrid_fetch.json
    ```
*   **측정 지표**: latency(p50/p95/p99), throughput(QPS), error rate, hit@k.
*   **부하 방식**: Closed-loop 방식 (worker N개).

### 6.6 Metrics 유틸 (`metrics.py`)
*   percentile 계산(p50/p95/p99), QPS 계산, bench 결과 dict 반환.

### 6.7 README 보강
*   데이터 생성, indexer 실행, 질의 생성, 벤치 실행 시나리오 및 데모 포인트 설명 추가.

### 6.8 구현 시 주의사항
*   외부 데이터/API 사용 금지.
*   seed 고정 시 재현 가능해야 함.
*   embedding은 기존 `embed_text_stub()` (또는 설정된 모델) 사용.
*   코드 가독성 중시.

### 6.9 최종 산출물
*   확장된 `app/` 코드.
*   `data/manifest.json`, `data/queries.jsonl`.
*   `out/bench_*.json` 벤치 결과.
*   업데이트된 README.md.

