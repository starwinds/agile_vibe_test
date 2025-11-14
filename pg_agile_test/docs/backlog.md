# Product Backlog

## Epic 1: Vector DB 환경 구축
- **Story:** 개발자는 pgvector가 활성화된 PostgreSQL 데이터베이스를 사용하여 벡터 데이터를 저장하고 관리할 수 있다.
  - **Task:** Docker를 사용하여 PostgreSQL + pgvector 컨테이너 설정
  - **Task:** Python에서 데이터베이스에 연결하고 기본 테이블을 생성하는 스크립트 작성

## Epic 2: Embedding 기능 구현
- **Story:** 개발자는 텍스트를 입력하면 Sentence Transformer 모델을 통해 고정된 차원의 임베딩 벡터를 얻을 수 있다.
  - **Task:** `sentence-transformers` 라이브러리를 사용한 임베딩 함수 구현
  - **Task:** 임베딩 함수의 결과 벡터 차원을 검증하는 단위 테스트 작성

## Epic 3: 데이터 저장 및 검색 기능 구현
- **Story:** 개발자는 생성된 임베딩 벡터를 텍스트와 함께 DB에 저장하고, 주어진 벡터와 유사한 데이터를 검색할 수 있다.
  - **Task:** 임베딩 데이터를 `docs` 테이블에 삽입하는 함수 구현
  - **Task:** 코사인 유사도를 사용하여 가장 유사한 데이터를 찾는 검색 함수 구현
  - **Task:** 데이터 삽입 및 검색 흐름을 검증하는 통합 테스트 작성

## Epic 4: TDD 및 Agile 개발 환경 구성
- **Story:** 개발자는 프로젝트 초기부터 TDD와 Agile 방법론을 적용할 수 있는 환경을 갖춘다.
  - **Task:** `pytest` 및 `pytest-cov`를 포함한 `requirements.txt` 파일 생성
  - **Task:** PRD, Backlog, Sprint Plan 등 Agile 문서 템플릿 생성
  - **Task:** 초기 프로젝트 구조(디렉토리, 파일) 설정

## Epic 5: 하이브리드 RDB + VectorDB 애플리케이션 개발
- **Story:** 사용자는 관계형 데이터(예: 상품명, 카테고리)와 비정형 데이터(예: 상품 설명)를 함께 저장하고, 두 가지 방식을 모두 활용하여 데이터를 검색할 수 있다.
  - **Task:** 기존 `docs` 테이블에 관계형 데이터(예: `item_name TEXT`, `category TEXT`)를 저장할 컬럼 추가
  - **Task:** Flask를 사용하여 새로운 아이템을 등록하는 API 엔드포인트 (`POST /item`) 구현
  - **Task:** 텍스트 유사도 검색과 관계형 데이터 필터링을 결합한 복합 검색 API 엔드포인트 (`GET /search`) 구현
  - **Task:** 신규 API 엔드포인트에 대한 통합 테스트 작성
  - **Task:** (Optional) API와 상호작용할 수 있는 간단한 웹 프론트엔드 페이지 작성
