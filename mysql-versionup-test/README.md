# MySQL 버전 업그레이드 호환성 테스트

이 프로젝트는 MySQL의 두 가지 다른 버전(8.0 및 8.4) 간의 호환성을 테스트하고 시스템 변수 차이를 비교하기 위해 구성되었습니다.

## 주요 기능

- **시스템 변수 비교**: 두 MySQL 버전의 시스템 변수를 비교하여 차이점을 보고서로 생성합니다.
- **자동화된 기능 테스트**: `tests/` 디렉토리에 포함된 기능 테스트들을 실행하고 결과를 JSON 파일로 저장합니다.

## 사용 방법

모든 테스트는 Docker 환경에서 실행되며, 상세한 설정 및 실행 절차는 아래 가이드를 참조하십시오.

- **[전체 테스트 수동 가이드](./docs/manual_test_guide.md)**

### 빠른 시작

1.  **데이터베이스 시작**
    ```bash
    cd mysql-compare
    docker-compose up -d
    ```

2.  **Python 환경 설정 및 스크립트 실행**
    ```bash
    cd python
    # 가상환경 생성 및 활성화
    python3 -m venv venv
    source venv/bin/activate
    # 의존성 설치
    pip install -r requirements.txt
    ```

3.  **스크립트 실행**
    -   **변수 비교 실행:**
        ```bash
        python compare_variables.py
        python generate_report.py
        ```
    -   **자동화 테스트 실행:**
        ```bash
        python run_tests.py
        ```

상세한 내용은 수동 가이드를 참고해 주세요.
