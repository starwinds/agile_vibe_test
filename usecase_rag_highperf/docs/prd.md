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

### 4.3 데이터베이스 스키마 (`postgres/`)
*   **Extensions**: `vector` 확장 설치
*   **Tables**:
    *   `documents`: 문서 메타데이터 (doc_id, tenant_id, title, version 등)
    *   `chunks`: 문서 청크 데이터 (chunk_id, doc_id, chunk_text, chunk_hash 등)
    *   `doc_acl`: 문서 접근 제어 목록 (tenant_id, doc_id, principal, permission)
    *   `outbox_events`: 데이터 변경 이벤트 저장 (Transactional Outbox 패턴 적용)

### 4.4 애플리케이션 로직 (`app/`)
*   **`common.py`**: 임베딩 차원 정의 및 Stub 임베딩 생성 함수, 바이너리 패킹 함수 제공.
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
