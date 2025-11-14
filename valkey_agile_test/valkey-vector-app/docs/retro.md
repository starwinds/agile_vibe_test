# Retrospective - Sprint 1: 환경 설정 및 기본 기능 구현

## 1. 잘된 점 (What went well?)
- **문제 해결 능력:** Valkey Docker 이미지 문제, `redis-py` 라이브러리와 Valkey VectorSearch 모듈 간의 호환성 문제 등 다양한 기술적 난관을 성공적으로 해결했습니다.
- **TDD 접근 방식:** 테스트 코드를 먼저 작성하고 이를 통과시키기 위해 코드를 수정하는 TDD 방식이 문제 해결 과정에서 명확한 목표를 제시하고 진행 상황을 검증하는 데 큰 도움이 되었습니다.
- **Agile 문서화:** 스프린트 진행 상황을 PRD, Backlog, Sprint Plan, Progress, Retro 문서로 체계적으로 기록하여 투명성을 확보하고 다음 스프린트 계획에 기여할 수 있게 되었습니다.
- **환경 설정 자동화:** Python 가상 환경, 의존성 설치, Docker 컨테이너 실행 등 초기 환경 설정 과정을 자동화하여 반복적인 작업을 줄였습니다.

## 2. 개선점 (What could be improved?)
- **초기 정보 부족:** Valkey VectorSearch 모듈의 특정 버전 또는 `valkey-bundle` 이미지에 대한 `redis-py` 라이브러리의 호환성 정보가 부족하여 문제 해결에 시간이 소요되었습니다. (예: `TEXT` 필드 타입, `sort_by`, `dialect` 인자)
    - **개선 방안:** 새로운 기술 스택 도입 시, 공식 문서 외에 커뮤니티 포럼이나 관련 이슈 트래커를 미리 확인하여 잠재적인 호환성 문제를 파악하는 시간을 더 할애해야 합니다.
- **테스트 환경의 견고성:** `Index already exists`와 같은 테스트 환경 관련 오류가 발생하여 테스트 코드 자체를 수정해야 했습니다.
    - **개선 방안:** 테스트 환경을 더욱 견고하게 구축하기 위해, 테스트 시작 전 DB 상태를 완전히 초기화하는 전역 Fixture 또는 Setup/Teardown 로직을 고려해야 합니다.

## 3. 다음 스프린트 액션 아이템 (Action Items for Next Sprint)
- **Valkey VectorSearch 공식 문서 심층 분석:** `valkey-bundle` 이미지에 포함된 RediSearch 모듈의 정확한 버전과 지원하는 명령 및 인자 목록을 파악하여 `redis-py` 사용 시 발생할 수 있는 호환성 문제를 최소화합니다.
- **Flask 웹 애플리케이션 개발 시작:** `src/app.py`에 Flask 웹 서버를 구축하고, 임베딩 생성 및 검색 API 엔드포인트를 구현합니다.
- **README.md 업데이트:** 프로젝트의 목적, 설치 및 실행 방법, 주요 기능 등을 상세히 기술하여 프로젝트 사용자가 쉽게 이해하고 활용할 수 있도록 합니다.
