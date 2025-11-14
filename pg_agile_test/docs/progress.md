# Sprint Progress

| 날짜       | 작업 내용                                       | 테스트 결과 | 커버리지 | 비고 |
|------------|-------------------------------------------------|-------------|----------|------|
| 2025-11-08 | 프로젝트 초기 설정 (Docker, Python, Agile 문서) | -           | -        | Gemini CLI를 통해 자동 생성 |
|            | `embedding.py` 스켈레톤 코드 작성               |             |          |      |
|            | `db_utils.py` 스켈레톤 코드 작성                |             |          |      |
|            | `test_embedding.py` 테스트 스켈레톤 작성        |             |          |      |
|            | `test_db.py` 테스트 스켈레톤 작성               |             |          |      |
| 2025-11-08 | 유클리드 거리 검색 기능 추가 (`search_similar_euclidean`) | 3 passed    | 100%     | TDD 사이클: 테스트 추가 -> 기능 구현 -> 테스트 통과 |
|            | `test_db_search_euclidean` 테스트 케이스 추가     |             |          |      |
| 2025-11-12 | `setup_pgvector_app.md` 문서 기반 테스트 진행 및 버그 수정. 주요 내용은 아래와 같음: <br> - `ModuleNotFoundError` 해결 <br> - DB 연결 오류 해결 <br> - `pgvector` 타입 등록 오류 해결 <br> - `test_search_endpoint` 실패 수정 | 5 passed    | 88%      | 모든 테스트 통과 |
| 2025-11-13 | Sprint 2 기능 구현 완료 및 테스트 검증. 주요 내용은 아래와 같음: <br> - `pytest.ini` 설정 및 `db_utils` 리팩토링으로 테스트 환경 오류 해결 <br> - `POST /item`, `GET /search` API 엔드포인트 테스트 통과 <br> - `pytest` Fixture를 통한 테스트 격리 최종 확인 | 5 passed    | 89%      | Sprint 2 백로그의 모든 기능 및 테스트 구현 완료 |