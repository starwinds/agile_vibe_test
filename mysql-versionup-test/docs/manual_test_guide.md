# MySQL 버전 비교 테스트 수동 가이드

이 문서는 `mysql-compare` 프로젝트의 테스트를 수동으로 실행하는 방법을 안내합니다.

이 테스트는 두 개의 다른 MySQL 버전(8.0 및 8.4)을 Docker 컨테이너로 실행하고, Python 스크립트를 사용하여 두 데이터베이스의 시스템 변수를 비교하고 결과를 보고서로 생성하는 과정을 포함합니다.

## 사전 준비 사항

- [Docker](https://www.docker.com/get-started) 및 `docker-compose`
- [Python 3](https://www.python.org/downloads/) (`pip` 포함)

## 1단계: 데이터베이스 환경 시작

테스트를 위해 비교할 두 버전의 MySQL 데이터베이스를 Docker 컨테이너로 시작해야 합니다.

1.  터미널을 열고 `mysql-compare` 디렉토리로 이동합니다.
    ```bash
    cd mysql-versionup-test/mysql-compare
    ```

2.  `docker-compose`를 사용하여 백그라운드에서 MySQL 컨테이너를 시작합니다.
    ```bash
    docker-compose up -d
    ```
    이 명령은 `mysql80` (MySQL 8.0)과 `mysql84` (MySQL 8.4) 두 개의 서비스를 시작합니다.

3.  컨테이너가 정상적으로 실행 중인지 확인합니다.
    ```bash
    docker-compose ps
    ```
    두 컨테이너의 `State`가 `Up`으로 표시되어야 합니다.

## 2단계: Python 실행 환경 설정

비교 스크립트를 실행하기 위해 Python 가상 환경을 설정하고 필요한 라이브러리를 설치합니다.

1.  `python` 디렉토리로 이동합니다.
    ```bash
    cd python
    ```

2.  Python 가상 환경을 생성합니다.
    ```bash
    python3 -m venv venv
    ```

3.  가상 환경을 활성화합니다.
    -   **macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```
    -   **Windows:**
        ```bash
        venv\Scripts\activate
        ```

4.  `requirements.txt` 파일에 명시된 Python 패키지를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

## 3단계: 변수 비교 스크립트 실행

이제 두 MySQL 데이터베이스의 변수를 비교하고 보고서를 생성하는 스크립트를 실행합니다.

1.  **변수 비교 스크립트 실행**

    `compare_variables.py` 스크립트는 두 데이터베이스에 연결하여 시스템 변수를 가져와 비교하고, 차이점을 `variable_comparison.json` 파일로 저장합니다.
    ```bash
    python compare_variables.py
    ```
    스크립트 실행이 완료되면 `variable_comparison.json` 파일이 생성된 것을 확인할 수 있습니다.

2.  **보고서 생성 스크립트 실행**

    `generate_report.py` 스크립트는 `variable_comparison.json` 파일을 읽어 `mysql_variable_comparison_report.md`라는 이름의 Markdown 형식 보고서를 생성합니다.
    ```bash
    python generate_report.py
    ```

## 4단계: 자동화된 테스트 스크립트 실행

`tests/` 디렉토리에 포함된 개별 기능 테스트들을 한 번에 실행하고 결과를 JSON 파일로 저장할 수 있습니다.

1.  `run_tests.py` 스크립트를 실행합니다.
    ```bash
    python run_tests.py
    ```

2.  스크립트는 `tests` 디렉토리의 모든 테스트(`test_*.py`)를 실행하고, 각 테스트의 성공/실패 여부, 출력, 실행 시간 등의 결과를 종합합니다.

3.  실행이 완료되면, 결과는 `test_results` 디렉토리 안에 `test_results_YYYYMMDD_HHMMSS.json` 형식의 파일로 저장됩니다. 이 파일을 열어 각 테스트의 상세 결과를 확인할 수 있습니다.

## 5단계: 결과 확인

모든 과정이 완료되면 생성된 보고서 파일을 확인합니다.

1.  `python` 디렉토리 내에 생성된 `mysql_variable_comparison_report.md` 파일을 엽니다.
2.  이 파일에는 두 MySQL 버전 간에 값이 다르거나 한 쪽에만 존재하는 시스템 변수들의 목록이 정리되어 있습니다.

## 6단계: 환경 정리

테스트가 완료된 후에는 Docker 컨테이너를 중지하고 제거하여 시스템 리소스를 정리합니다.

1.  `mysql-compare` 디렉토리로 돌아갑니다.
    ```bash
    cd ..
    ```

2.  `docker-compose`를 사용하여 컨테이너를 중지하고 관련 네트워크와 볼륨을 제거합니다.
    ```bash
    docker-compose down
    ```

3.  Python 가상 환경을 비활성화하려면 다음 명령을 실행합니다.
    ```bash
    deactivate
    ```
