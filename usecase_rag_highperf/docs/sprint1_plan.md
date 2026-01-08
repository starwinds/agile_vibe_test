# Sprint 1 Plan: RAG High-Perf MVP 구축

## 1. 스프린트 개요
*   **목표**: Postgres(SoR)와 Valkey(Vector Search)를 연동한 고성능 RAG 시스템의 MVP를 구축하고, 데이터 적재부터 검색까지의 End-to-End 흐름을 검증한다.
*   **기간**: 1주 (예상)
*   **참여자**: 개발자 1명 (AI Assistant 포함)

## 2. 스프린트 목표 (Sprint Goal)
1.  Docker Compose 기반의 로컬 개발 환경(Postgres 16.9 + Valkey)을 완벽하게 구성한다.
2.  Python 애플리케이션을 통해 문서 Ingest, Indexing, Query 기능을 구현한다.
3.  실제 샘플 데이터를 사용하여 검색 결과와 ACL 동작을 검증한다.

## 3. 대상 백로그 아이템 (Selected Backlog Items)

### Epic 1: 인프라 및 환경 구성
*   **INFRA-001**: Docker Compose 구성 (Postgres 16.9, Valkey)
*   **INFRA-002**: 환경 변수 설정 (.env)

### Epic 2: 데이터베이스 모델링
*   **DB-001**: 확장(vector) 및 스키마(documents, chunks, doc_acl, outbox_events) 스크립트 작성

### Epic 3: 애플리케이션 개발
*   **APP-001**: 공통 모듈(common.py) 및 의존성(requirements.txt) 구성
*   **APP-002**: Ingest 서비스(ingest.py) 구현 (청킹, DB저장, 이벤트발행)
*   **APP-003**: Indexer 서비스(indexer.py) 구현 (이벤트소비, 임베딩, Valkey색인)
*   **APP-004**: Query 서비스(query.py) 구현 (임베딩, KNN검색, ACL필터링)
*   **APP-005**: Healthcheck 스크립트(healthcheck.py) 구현

### Epic 4: 검증 및 문서화
*   **VER-001**: End-to-End 테스트 수행 (Ingest -> Index -> Query)
*   **VER-002**: README 작성 (실행 가이드)

## 4. 완료 조건 (Definition of Done)
*   모든 코드는 `usecase_rag_highperf` 디렉토리 내에 작성되어야 한다.
*   `docker compose up` 명령으로 에러 없이 컨테이너가 실행되어야 한다.
*   `healthcheck.py` 실행 시 Postgres와 Valkey가 모두 정상(OK)이어야 한다.
*   `ingest.py` 실행 후 `indexer.py`를 통해 Valkey에 키가 생성되어야 한다.
*   `query.py` 실행 시 검색 결과가 반환되고, 권한에 맞는 본문이 출력되어야 한다.
*   README.md에 따라 제3자가 실행했을 때 동일한 결과가 나와야 한다.

## 5. 일일 계획 (Rough Schedule)
*   **Day 1**: 인프라 구성 (INFRA-001, INFRA-002) 및 DB 스키마 작성 (DB-001)
*   **Day 2**: 공통 모듈 (APP-001) 및 Ingest 구현 (APP-002)
*   **Day 3**: Indexer 구현 (APP-003) 및 Healthcheck (APP-005)
*   **Day 4**: Query 구현 (APP-004) 및 통합 테스트
*   **Day 5**: 문서화 (VER-002) 및 최종 리팩토링
