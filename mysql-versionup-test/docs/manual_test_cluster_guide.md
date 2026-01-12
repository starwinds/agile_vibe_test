# MySQL InnoDB Cluster 버전 비교 테스트 수동 가이드

이 문서는 MySQL 8.0과 8.4의 **InnoDB Cluster** 환경을 구축하고, Primary 노드 설정을 비교하여 통합 리포트를 생성하는 수동 테스트 절차를 안내합니다.

## 사전 준비 사항

- [Docker](https://www.docker.com/get-started) 및 `docker-compose`
- [Python 3](https://www.python.org/downloads/) (`pip` 포함)
- **Standalone 테스트 결과**: 통합 리포트 생성을 위해 기존 Standalone 테스트(`compare_variables.py`)가 먼저 실행되어 `variable_comparison.json` 파일이 존재해야 합니다.

## 1단계: Cluster 환경 시작

InnoDB Cluster 테스트를 위한 별도의 Docker Compose 구성을 사용하여 컨테이너를 실행합니다.

1.  터미널을 열고 `mysql-compare` 디렉토리로 이동합니다.
    ```bash
    cd mysql-versionup-test/mysql-compare
    ```

2.  `docker-compose.cluster.yml` 파일을 지정하여 클러스터 환경을 시작합니다.
    ```bash
    docker-compose -f docker-compose.cluster.yml up -d
    ```
    이 명령은 다음 컨테이너들을 실행합니다:
    - MySQL 8.0 노드 3개 (`mysql80-1`, `mysql80-2`, `mysql80-3`)
    - MySQL 8.4 노드 3개 (`mysql84-1`, `mysql84-2`, `mysql84-3`)
    - 클러스터 설정용 MySQL Shell (`cluster-setup`)

3.  컨테이너 상태를 확인합니다.
    ```bash
    docker-compose -f docker-compose.cluster.yml ps
    ```

## 2단계: InnoDB Cluster 부트스트랩 (Cluster 구성)

컨테이너가 실행된 직후에는 아직 클러스터가 구성되지 않은 상태입니다. 준비된 스크립트를 통해 자동으로 클러스터를 구성합니다.

1.  `cluster-setup` 컨테이너를 통해 설정 스크립트를 실행합니다.
    ```bash
    docker exec -it cluster-setup mysqlsh --py --file /script/cluster_setup.py
    ```
    - 이 스크립트는 MySQL 8.0과 8.4 각각에 대해 Primary 1개 + Secondary 2개로 구성된 InnoDB Cluster를 생성합니다.
    - 실행 중 "Cluster created successfully" 및 각 노드가 "successfully added" 되었다는 메시지를 확인하세요.

## 3단계: Python 환경 설정

(이미 설정되어 있다면 이 단계는 건너뛰세요)

1.  `python` 디렉토리로 이동합니다.
    ```bash
    cd python
    ```

2.  가상 환경 활성화 및 의존성 설치:
    ```bash
    # Linux/macOS
    source .venv/bin/activate
    
    # 의존성 설치
    pip install -r requirements.txt
    ```

## 4단계: Cluster 비교 테스트 실행

Primary 노드를 자동으로 식별하고 시스템 변수를 비교하는 테스트를 실행합니다.

1.  `pytest`를 사용하여 Cluster 변수 비교 테스트를 실행합니다.
    ```bash
    pytest tests/test_cluster_variables.py
    ```

2.  **결과 확인**:
    - 테스트가 통과(Passed)하면 `cluster_variable_comparison.json` 파일이 `mysql-compare/python` 디렉토리에 생성됩니다.
    - 이 파일에는 MySQL 8.0과 8.4 Primary 노드 간의 Global Variables 비교 결과가 저장됩니다.

## 5단계: 통합 리포트 생성

Standalone 테스트 결과와 Cluster 테스트 결과를 합쳐서 최종 리포트를 생성합니다.

1.  **전제 조건 확인**:
    - 같은 디렉토리에 `variable_comparison.json` (Standalone 결과)과 `cluster_variable_comparison.json` (Cluster 결과) 파일이 모두 있는지 확인합니다.
    - 만약 `variable_comparison.json`이 없다면, `python compare_variables.py` (Standalone 환경 실행 필요)를 수행해야 할 수 있습니다.

2.  리포트 생성 스크립트 실행:
    ```bash
    python generate_new_report.py
    ```

3.  **리포트 확인**:
    - `mysql-versionup-test/docs/mysql_version_diff_test_new_report.md` 파일이 생성됩니다.
    - 이 리포트에서 **Version-driven Diff** (버전 차이)와 **Cluster-driven Diff** (클러스터 환경 차이)가 구분되어 있는지 확인하세요.

## 6단계: 환경 정리

테스트 완료 후 리소스를 정리합니다.

1.  `mysql-compare` 디렉토리로 이동하여 클러스터 환경을 종료합니다.
    ```bash
    cd ..
    docker-compose -f docker-compose.cluster.yml down -v
    ```
    - `-v` 옵션은 볼륨까지 삭제하여 데이터를 초기화합니다. 다음 테스트 시 깨끗한 환경에서 시작하기 위해 권장됩니다.
