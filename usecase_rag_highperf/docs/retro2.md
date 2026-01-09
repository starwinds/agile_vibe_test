# Sprint 2 Retrospective: Ollama 임베딩 연동

## 1. 스프린트 개요
*   **기간**: 1주
*   **목표**: Stub 임베딩 제거 및 Ollama (`nomic-embed-text`) 연동을 통한 실제 RAG 시스템 구현.

## 2. 목표 달성 여부 (Goal Achievement)
*   [x] **Ollama 환경 설정**: `.env`에 `OLLAMA_BASE_URL` 설정 완료.
*   [x] **애플리케이션 연동**: `common.py`에서 `requests`를 사용하여 Ollama API 호출 구현 완료. `EMBED_DIM`을 768로 변경.
*   [x] **호환성 확인**: `indexer.py`에서 차원 불일치 시 인덱스 재생성 로직 확인.
*   [x] **End-to-End 테스트**: `ingest.py` -> `indexer.py` -> `query.py` 흐름 정상 동작 확인.

## 3. 잘된 점 (What Went Well)
*   **모듈화된 설계**: `common.py`에 임베딩 로직이 집중되어 있어, `ingest`, `indexer`, `query` 서비스의 코드 수정 없이 임베딩 모델 교체가 용이했음.
*   **비동기 인덱싱**: `indexer.py`가 Outbox 패턴을 통해 비동기로 동작하여, 임베딩 생성 시간이 길어져도 Ingest 요청에 영향을 주지 않음.

## 4. 아쉬운 점 / 개선할 점 (What Could Be Improved)
*   **의존성 관리**: 테스트 스크립트 실행 시 `python-dotenv` 등의 의존성이 가상환경(`.venv`)에만 설치되어 있어, 실행 환경 확인이 필요했음.
*   **에러 처리**: Ollama 서비스가 내려가 있을 경우 `indexer.py`에서 예외가 발생하고 재시도하는 로직이 단순함 (Fail Fast). 좀 더 견고한 재시도 정책(Exponential Backoff) 고려 필요.

## 5. Action Items
*   [ ] 다음 스프린트에서 `indexer.py`의 에러 핸들링 및 재시도 로직 강화.
*   [ ] CI/CD 파이프라인에 Ollama 서비스 헬스 체크 추가 고려.
