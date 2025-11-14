# Product Backlog for Valkey VectorSearch App

## Epic: 환경 설정 및 기본 기능 구현 (완료)
- **Story:** Valkey VectorSearch 환경 구축
    - **Task:** Valkey Docker 컨테이너 실행 (`valkey/valkey-bundle` 사용)
    - **Task:** Python 가상 환경 설정 및 의존성 설치
    - **Task:** 프로젝트 디렉토리 구조 생성
    - **Task:** `src/embedding.py` 스켈레톤 코드 작성
    - **Task:** `src/db_utils.py` 스켈레톤 코드 작성
    - **Task:** `tests/test_embedding.py` 테스트 코드 작성
    - **Task:** `tests/test_db.py` 테스트 코드 작성
    - **Task:** `redis-py`와 Valkey VectorSearch 모듈 간의 호환성 문제 해결 (TEXT -> TAG, sort_by, dialect)
    - **Task:** 테스트 코드 실행 및 모든 테스트 통과 확인

## Epic: 웹 애플리케이션 인터페이스 (진행 예정)
- **Story:** Flask 기반 웹 서버 구축
    - **Task:** `src/app.py`에 Flask 애플리케이션 초기화 코드 작성
    - **Task:** Valkey 연결 설정
    - **Task:** 임베딩 생성 및 저장 API 엔드포인트 구현
    - **Task:** 벡터 검색 API 엔드포인트 구현
    - **Task:** 간단한 웹 UI (HTML/CSS) 구현 (선택 사항)
    - **Task:** 웹 애플리케이션 테스트 코드 작성

## Epic: 배포 및 운영 (진행 예정)
- **Story:** Docker Compose를 이용한 배포 자동화
    - **Task:** `docker-compose.yml` 파일 작성
    - **Task:** Valkey 및 Python 앱 컨테이너 정의
    - **Task:** 배포 스크립트 작성
- **Story:** 모니터링 및 로깅
    - **Task:** 애플리케이션 로깅 설정
    - **Task:** Valkey 모니터링 지표 확인

## Epic: 성능 최적화 (진행 예정)
- **Story:** 임베딩 모델 최적화
    - **Task:** 더 효율적인 임베딩 모델 탐색 및 적용
- **Story:** Valkey 인덱스 최적화
    - **Task:** 인덱스 파라미터 튜닝

## Epic: 문서화 (진행 예정)
- **Story:** README.md 업데이트
    - **Task:** 프로젝트 소개, 설치 및 실행 방법, API 문서 추가
- **Story:** 개발 가이드 문서 (`dev_guide.txt`) 상세화
    - **Task:** TDD 개발 프로세스 상세 설명
    - **Task:** 코드 컨벤션 및 스타일 가이드 추가
