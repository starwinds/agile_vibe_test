# Sprint 2 Plan: Web Application Development

## 1. 스프린트 기간 (Sprint Period)
- **기간:** 2025년 11월 17일 ~ 2025년 11월 21일 (1주)

## 2. 스프린트 목표 (Sprint Goal)
- Valkey 벡터 검색 기능을 활용하는 QA 서비스를 위한 웹 애플리케이션의 핵심 기능을 개발하고 사용자에게 제공한다.
- 사용자가 웹 인터페이스를 통해 질문하고, 문서를 추가할 수 있는 기본적인 UI와 API를 구현한다.

## 3. 팀 용량 (Capacity)
- 개발자 1인 (Gemini)이 웹 애플리케이션 개발에 집중적으로 참여한다.

## 4. 완료의 정의 (Definition of Done - DoD)
- 모든 코드는 `main` 브랜치에 병합되어야 한다.
- 모든 기능은 단위 및 통합 테스트를 통과해야 한다.
- 테스트 커버리지는 80% 이상을 유지해야 한다.
- 새로운 API 엔드포인트는 문서화되어야 한다.
- UI는 기본적인 스타일링을 포함하며, 주요 브라우저에서 작동해야 한다.

## 5. 스프린트 백로그 (Sprint Backlog)

### Epic: Web Application for QA Service

- **Story 1: API 개발 (Backend)**
    - **Task 1.1:** Flask 애플리케이션 기본 구조(`app.py`) 설정.
    - **Task 1.2:** 질문/답변을 위한 `/qa` API 엔드포인트 구현.
    - **Task 1.3:** 새 문서 추가를 위한 `/add_document` API 엔드포인트 구현.
    - **Task 1.4:** API 엔드포인트에 대한 단위 및 통합 테스트 작성.

- **Story 2: 사용자 인터페이스 개발 (Frontend)**
    - **Task 2.1:** 질문을 입력하고 답변을 표시하는 기본 HTML 페이지 생성.
    - **Task 2.2:** 문서 업로드를 위한 파일 입력 폼이 있는 HTML 페이지 생성.
    - **Task 2.3:** JavaScript를 사용하여 프론트엔드와 백엔드 API 연동.
    - **Task 2.4:** 간단한 CSS를 적용하여 사용자 경험 개선.
