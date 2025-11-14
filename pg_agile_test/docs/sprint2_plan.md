# Sprint 2 Plan

## Sprint 기간
- **시작일:** 2025년 11월 8일
- **종료일:** 2025년 11월 21일

## Sprint 목표
- PostgreSQL을 관계형 데이터베이스(RDB)와 벡터 데이터베이스(VectorDB)로 동시에 활용하는 하이브리드 애플리케이션의 기반을 구축한다.
- 아이템을 등록하고, 관계형 데이터 필터와 벡터 유사도 검색을 결합한 복합 검색 기능을 API로 제공한다.
- Sprint 1의 회고에서 도출된 액션 아이템(Fixture 사용 등)을 적용하여 테스트 품질을 개선한다.

## Sprint Backlog (from Epic 5)
1.  **Task 1:** `docs` 테이블 스키마 변경 (관계형 컬럼 추가) 및 `db_utils` 업데이트
2.  **Task 2:** `pytest` Fixture를 사용하여 테스트 간 데이터베이스 상태 격리
3.  **Task 3:** Flask `app.py` 기본 설정 및 아이템 등록 API (`POST /item`) 구현
4.  **Task 4:** 아이템 등록 API에 대한 통합 테스트 작성
5.  **Task 5:** 복합 검색 API (`GET /search`) 구현
6.  **Task 6:** 복합 검색 API에 대한 통합 테스트 작성

## Definition of Done (DoD)
- Sprint Backlog의 모든 Task가 완료되어야 한다.
- 모든 API 엔드포인트는 `pytest`를 통해 테스트되어야 한다.
- 테스트 커버리지는 90% 이상을 유지해야 한다.
- API 사용법이 `README.md`에 문서화되어야 한다.
- 모든 작업은 `docs/progress.md`에 기록되어야 한다.
