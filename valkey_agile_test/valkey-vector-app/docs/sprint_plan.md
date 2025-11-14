# Sprint Plan - Sprint 1: 환경 설정 및 기본 기능 구현

## 1. 스프린트 기간
- **시작일:** 2025년 11월 13일
- **종료일:** 2025년 11월 14일 (1일 스프린트)

## 2. 스프린트 목표
- Valkey VectorSearch 개발 환경을 완벽하게 구축하고, 핵심 임베딩 및 DB 유틸리티 기능의 단위 테스트를 모두 통과시킨다.
- `redis-py` 라이브러리와 Valkey VectorSearch 모듈 간의 초기 호환성 문제를 해결하고 안정적인 기반을 마련한다.

## 3. Capacity
- Gemini CLI Agent: 100% (전담)

## 4. Definition of Done (DoD)
- Valkey Docker 컨테이너 (`valkey/valkey-bundle`)가 성공적으로 실행되고 접근 가능해야 한다.
- Python 가상 환경이 설정되고 `requirements.txt`의 모든 의존성이 설치되어야 한다.
- 프로젝트 구조가 `docs/setup_valkey_vector_app.md`에 명시된 대로 생성되어야 한다.
- `src/embedding.py` 및 `src/db_utils.py`의 스켈레톤 코드가 작성되어야 한다.
- `tests/test_embedding.py` 및 `tests/test_db.py`의 테스트 코드가 작성되어야 한다.
- `pytest --cov=src -v` 명령을 실행했을 때 모든 테스트가 성공적으로 통과해야 한다.
- `ModuleNotFoundError`, `ConnectionRefusedError`, `AttributeError`, `TypeError`, `ResponseError` 등 환경 설정 및 초기 코드 관련 모든 오류가 해결되어야 한다.
- `docs/prd.md`, `docs/backlog.md`, `docs/sprint_plan.md`, `docs/progress.md`, `docs/retro.md` 파일이 생성되어야 한다.

## 5. 스프린트 백로그 (Sprint Backlog)

### Epic: 환경 설정 및 기본 기능 구현
- **Story:** Valkey VectorSearch 환경 구축 (완료)
    - **Task:** Valkey Docker 컨테이너 실행 (`valkey/valkey-bundle` 사용)
    - **Task:** Python 가상 환경 설정 및 의존성 설치
    - **Task:** 프로젝트 디렉토리 구조 생성
    - **Task:** `src/embedding.py` 스켈레톤 코드 작성
    - **Task:** `src/db_utils.py` 스켈레톤 코드 작성
    - **Task:** `tests/test_embedding.py` 테스트 코드 작성
    - **Task:** `tests/test_db.py` 테스트 코드 작성
    - **Task:** `redis-py`와 Valkey VectorSearch 모듈 간의 호환성 문제 해결 (TEXT -> TAG, sort_by, dialect)
    - **Task:** 테스트 코드 실행 및 모든 테스트 통과 확인
    - **Task:** Agile 문서 세트 생성 (`prd.md`, `backlog.md`, `sprint_plan.md`, `progress.md`, `retro.md`)
