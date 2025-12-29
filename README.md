# Agile Vibe Test 프로젝트 개요 

이 프로젝트는 다양한 DBMS(RDB-mysql,postgresql 등, Cache-valkey 등)의 기능 및 성능 검증을 위한 테스트 자동화와 보고서 생성을 목적으로 합니다.
- 테스트의 대상 별로 sub 프로젝트를 별도로 만들어서 진행합니다. 
- AI Assitant(gemini-cli, anti-gravitiy, cursor등)와의 협업을 통해 진행하며, 프로젝트 진행 방식은 기본적으로 Agile 개발 방법론을 따릅니다. 
- AI Assistant와의 협업 관계는 아래와 같습니다. 
    - 프로젝트 PM/기획/설계/품질 담당: human(steve.woo)
    - 기술검토/설계/개발/QA 수행 담당: AI Assistant(gemini-cli, anti-gravitiy, cursor등) 
- 프로젝트는 아래와 같은 문서를 생성하며, 관련 가이드를 준수합니다.
    - Agile 개발 방법론 기반 문서: 개별 sub 프로젝트별로 docs 디렉토리에 아래와 같은 문서 생성 
        - prod.md: 각 sub 프로젝트의 요구 사항 명세 
        - backlog.md: 각 sub 프로젝트의 backlog 명세 
        - sprint_plan.md: 각 sub 프로젝트의 sprint plan 명세 
        - retro.md: 각 sub 프로젝트의 sprint 후기 명세    
    - 개발 Task는 기본적으로 아래 가이드를 준수합니다.    
        - dev_guide.txt: kent beck의 TDD 기반 개발 가이드          

## 프로젝트 구조

이 저장소는 여러 하위 프로젝트로 나뉩니다:

-   `pg_agile_test/`: **PostgreSQL + pgvector**를 사용하는 QA 서비스 구현체입니다.
-   `valkey_agile_test/`: **Valkey**를 사용하는 QA 서비스 구현체입니다.
-   `redis-valkey-compat/`: **Redis와 Valkey 간의 호환성**을 테스트하는 프로젝트입니다.
    -   `docs/comprehensive_test_report.md`: Redis 7.2.6과 Valkey 9.0.0 간의 상세 성능 및 호환성 테스트 결과를 포함합니다.
-   `valkey-ha-and-cluster/`: **Valkey의 고가용성(HA) 및 클러스터 모드**를 테스트하고 구현하는 프로젝트입니다.
-   `valkey-vector-benchmark/`: **VectorDBBench**를 확장하여 Valkey Vector Search 성능을 벤치마킹하는 프로젝트입니다. Standalone, HA, Cluster 모드를 모두 지원하며, 최근 클러스터 모드 벤치마크 설정이 개선되었습니다. ([가이드 보기](valkey-vector-benchmark/docs/manual_benchmark_guide.md))
-   `valkey-vector-search-test/`: Valkey의 벡터 검색 기능을 검증하는 간단한 테스트 프로젝트입니다.
-   `mysql-versionup-test/`: **MySQL 버전 간 호환성 및 성능 차이**를 자동으로 검증하는 프로젝트입니다.
    -   **듀얼 환경 구성:** Docker Compose를 사용하여 MySQL 8.0.42와 8.4.7(LTS) 환경을 동시에 구축하고 관리합니다.
    -   **자동화된 테스트 (`pytest`):** Python 기반의 테스트 프레임워크를 통해 두 버전 간의 차이점을 정량적/정성적으로 비교합니다.
        -   **인증 방식 검증:** 8.4에서 기본 비활성화된 `mysql_native_password`와 `caching_sha2_password`의 동작 차이를 검증합니다.
        -   **시스템 변수 전수 비교:** 600여 개의 시스템 변수를 전수 조사하여 값이 변경된 항목(예: `innodb_adaptive_hash_index`, `innodb_io_capacity` 등)과 추가/삭제된 변수를 식별합니다.
        -   **스키마 및 시스템 데이터베이스:** `information_schema`의 테이블/컬럼 변화 및 Foreign Key 제약 조건의 엄격함 차이(예: `restrict_fk_on_non_standard_key`)를 테스트합니다.
        -   **성능 벤치마크:** 간단한 Insert TPS 및 Select Latency 측정을 통해 버전 업그레이드에 따른 성능 경향성을 파악합니다.
    -   **자동 리포팅:** 테스트 실행 결과를 `test_results.json`으로 저장하고, 이를 바탕으로 시각화된 요약 보고서([mysql_version_diff_test_report.md](mysql-versionup-test/docs/mysql_version_diff_test_report.md))를 자동 생성합니다.

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
-   **Valkey Vector Search 벤치마크:** VectorDBBench를 확장하여 Valkey의 HNSW/FLAT 인덱스 성능을 Standalone, HA, Cluster 모드에서 측정합니다.
-   **Valkey Vector Search 기능 테스트:** 간단한 스크립트를 통해 Valkey의 벡터 검색 기능의 기본적인 동작을 검증합니다.
-   **MySQL 버전 간 비교 테스트:** MySQL 8.0과 8.4 간의 인증, 시스템 변수, 스키마 호환성 및 성능 차이를 자동으로 검증하고 리포트를 생성합니다.

## 기술 스택

-   **백엔드:** Python, Flask
-   **벡터 임베딩:** Hugging Face Transformers
-   **데이터베이스:**
    -   PostgreSQL (`pgvector` 확장 기능 포함)
    -   Valkey / Redis
    -   MySQL (8.0.42, 8.4.7)
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

### `mysql-versionup-test` (MySQL)

1.  **환경 구성:** `docker-compose.yml`을 사용하여 MySQL 8.0 및 8.4 컨테이너를 실행합니다.
    ```bash
    cd mysql-versionup-test/mysql-compare
    docker-compose up -d
    ```

2.  **테스트 실행:** `pytest`를 사용하여 자동화된 비교 테스트를 수행합니다.
    ```bash
    cd python
    pip install -r requirements.txt
    pytest tests/
    ```

3.  **리포트 생성:** 테스트 결과를 바탕으로 마크다운 보고서를 생성합니다.
    ```bash
    python generate_report.py
    ```

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