# Progress Report - Sprint 1: 환경 설정 및 기본 기능 구현

## 2025년 11월 13일 (목)

### 작업 내역
- Valkey Docker 컨테이너 실행 시 `valkey/valkey:latest` 이미지에서 `vectorsearch.so` 모듈 로드 실패 문제 발생.
    - **해결:** `valkey/valkey-bundle:latest` 이미지로 변경하여 컨테이너 재시작.
- Python 가상 환경 (`.venv`) 생성 및 `requirements.txt` 기반 의존성 설치.
- 프로젝트 디렉토리 구조 및 `src/embedding.py`, `src/db_utils.py` 스켈레톤 코드 작성.
- `tests/test_embedding.py`, `tests/test_db.py` 테스트 코드 작성.
- `pytest --cov=src -v` 실행 시 `ModuleNotFoundError: No module named 'src'` 발생.
    - **해결:** `setup.py` 파일 생성 후 `pip install -e .`로 프로젝트를 editable 모드로 설치하고, `PYTHONPATH=.` 환경 변수를 설정하여 테스트 실행.
- `test_db.py` 실행 시 `redis.exceptions.ResponseError: Invalid field type for field `content`: Unknown argument `TEXT`` 발생.
    - **해결:** `src/db_utils.py`에서 `TextField` 대신 `TagField` 사용하도록 수정.
- `test_db.py` 실행 시 `TypeError: SearchCommands.search() got an unexpected keyword argument 'sort_by'` 발생.
    - **해결:** `src/db_utils.py`에서 `Query` 객체의 `sort_by()` 메서드를 사용하도록 수정.
- `test_db.py` 실행 시 `TypeError: SearchCommands.search() got an unexpected keyword argument 'dialect'` 발생.
    - **해결:** `src/db_utils.py`에서 `search` 메서드 호출 시 `dialect=2` 인자 제거.
- `test_db.py` 실행 시 `redis.exceptions.ResponseError: Index doc_index already exists` 발생.
    - **해결:** `src/db_utils.py`의 `create_index` 함수에서 인덱스 존재 여부를 확인하고 없으면 생성하도록 로직 변경. `test_db.py`에서 `dropindex()` 호출 제거.
- 모든 테스트 통과 확인.
- Agile 문서 세트 (`prd.md`, `backlog.md`, `sprint_plan.md`, `progress.md`, `retro.md`) 작성.

### 테스트 결과
- `pytest --cov=src -v` 실행 결과:
    - `tests/test_db.py::test_db_insert_and_search PASSED`
    - `tests/test_embedding.py::test_embedding_shape PASSED`
    - **총 2개 테스트 통과, 0개 실패.**

### 커버리지
- `src/db_utils.py`: 90%
- `src/embedding.py`: 100%
- **TOTAL**: 93%
