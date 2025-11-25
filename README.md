# Agile Vibe QA 서비스

이 프로젝트는 벡터 유사도 검색을 사용하는 질의응답(QA) 서비스를 구현합니다. PostgreSQL의 `pgvector` 확장 기능을 사용하는 구현과 Valkey(Redis의 포크)를 벡터 데이터베이스로 사용하는 두 가지 개별 구현을 제공합니다.

## 프로젝트 구조

이 저장소는 여러 하위 프로젝트로 나뉩니다:

-   `pg_agile_test/`: **PostgreSQL + pgvector**를 사용하는 QA 서비스 구현체입니다.
-   `valkey_agile_test/`: **Valkey**를 사용하는 QA 서비스 구현체입니다.
-   `redis-valkey-compat/`: **Redis와 Valkey 간의 호환성**을 테스트하는 프로젝트입니다.
    -   `docs/comprehensive_test_report.md`: Redis 7.2.6과 Valkey 9.0.0 간의 상세 성능 및 호환성 테스트 결과를 포함합니다.
-   `valkey-ha-and-cluster/`: **Valkey의 고가용성(HA) 및 클러스터 모드**를 테스트하고 구현하는 프로젝트입니다.

각 프로젝트는 유사한 아키텍처를 공유하며 다음으로 구성됩니다:

-   주요 애플리케이션 로직을 포함하는 `src` 또는 `app` 디렉토리.
-   단위 테스트가 있는 `tests` 디렉토리 (해당하는 경우).
-   프로젝트 문서를 위한 `docs` 디렉토리.
-   Python 종속성을 나열하는 `requirements.txt` 파일.

## 기능

-   **질의응답:** 데이터베이스에 저장된 문서를 기반으로 질문하고 답변을 받습니다.
-   **문서 제출:** 기술 자료에 새 문서를 추가합니다.
-   **벡터 유사도 검색:** 벡터 임베딩을 활용하여 주어진 질문에 가장 관련성이 높은 문서를 찾습니다.
-   **Redis/Valkey 호환성 테스트:** 기본 CRUD, Pub/Sub, Lua 스크립트, 대용량 페이로드 처리 등 다양한 시나리오에서 호환성을 검증합니다.
-   **Valkey HA/클러스터:** Sentinel을 이용한 고가용성 구성과 클러스터 모드 구성을 테스트합니다.

## 기술 스택

-   **백엔드:** Python, Flask
-   **벡터 임베딩:** Hugging Face Transformers
-   **데이터베이스:**
    -   PostgreSQL (`pgvector` 확장 기능 포함)
    -   Valkey / Redis
-   **테스팅:** Pytest
-   **인프라:** Docker, Docker Compose

## 설치 및 사용법

### 일반 설정

1.  **저장소 복제:**
    ```bash
    git clone https://github.com/starwinds/agile_vibe_test.git
    cd agile_vibe_test
    ```

2.  **종속성 설치:** 각 하위 프로젝트에는 자체 `requirements.txt` 파일이 있습니다.
    ```bash
    # pg_agile_test 프로젝트의 경우
    pip install -r pg_agile_test/requirements.txt

    # valkey_agile_test 프로젝트의 경우
    pip install -r valkey_agile_test/valkey-vector-app/requirements.txt
    ```

### `pg_agile_test` (PostgreSQL + pgvector)

1.  **환경 변수 설정:**
    ```bash
    export PG_HOST=<your_postgres_host>
    export PG_PORT=<your_postgres_port>
    export PG_DBNAME=<your_postgres_db>
    export PG_USER=<your_postgres_user>
    export PG_PASSWORD=<your_postgres_password>
    ```

2.  **데이터베이스 초기화:** `pg_agile_test/src/db_utils.py`의 `init_db()` 함수를 실행하여 `documents` 테이블을 생성하고 `vector` 확장 기능을 활성화합니다.

3.  **Flask 애플리케이션 실행:**
    ```bash
    python pg_agile_test/src/app.py
    ```

### `valkey_agile_test` (Valkey)

1.  **환경 변수 설정:**
    ```bash
    export VALKEY_HOST=<your_valkey_host>
    export VALKEY_PORT=<your_valkey_port>
    ```

2.  **데이터베이스 초기화:** `valkey_agile_test/valkey-vector-app/src/db_utils.py`의 `init_db()` 함수를 실행하여 벡터 인덱스를 생성합니다.

3.  **Flask 애플리케이션 실행:** (참고: 현재 파일 구조를 기반으로 Valkey용 `app.py`는 아직 구현되지 않았습니다).

## API 엔드포인트

Flask 애플리케이션(`pg_agile_test`의 `app.py`)은 다음 엔드포인트를 제공합니다:

-   `POST /add_document`
    -   기술 자료에 새 문서를 추가합니다.
    -   **Body:** `{"document": "이것은 새 문서의 내용입니다."}`
-   `GET /qa`
    -   질문을 하고 가장 관련성이 높은 문서를 가져옵니다.
    -   **쿼리 매개변수:** `?question=문서의 내용은 무엇입니까?`

## 현재 상태

-   PostgreSQL 및 Valkey 모두에 대해 임베딩 생성 및 데이터베이스 상호 작용을 위한 핵심 기능이 구현되었습니다.
-   `pg_agile_test` 프로젝트를 위해 Flask 기반 웹 API가 구현되어 작동합니다.
-   데이터베이스 및 임베딩 모듈에 대한 단위 테스트가 마련되어 있습니다.
-   푸시 시 테스트를 실행하기 위해 GitHub Actions를 사용하는 CI/CD 파이프라인이 프로젝트에 설정되어 있습니다.