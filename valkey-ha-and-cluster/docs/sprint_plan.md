# Sprint 1: Valkey HA 및 Cluster 기본 환경 구축 및 테스트

## 1. 스프린트 정보

-   **스프린트 기간**: 2025년 11월 21일 ~ 2025년 11월 28일
-   **담당자**: Gemini CLI (Backend Infrastructure Engineer, Python Developer)

## 2. 스프린트 목표

이번 스프린트의 핵심 목표는 Valkey의 **HA(Master-Replica-Sentinel)** 구조와 **Cluster** 구조의 기본 인프라를 Docker Compose로 구축하고, 각 환경의 핵심 기능(자동 Failover, 데이터 분산)을 검증하는 Python 테스트 앱의 프로토타입을 완성하는 것입니다.

-   **목표 1**: `docker-compose.ha.yml`을 통해 HA 환경을 안정적으로 실행한다.
-   **목표 2**: `docker-compose.cluster.yml`을 통해 Cluster 환경을 안정적으로 실행한다.
-   **목표 3**: Python 테스트 스크립트(`ha_test.py`, `cluster_test.py`)의 기본 골격을 구현하고, 각 환경에 성공적으로 연결하여 기본 CRUD가 동작함을 확인한다.
-   **목표 4**: HA 환경의 자동 Failover 및 Cluster 환경의 `MOVED` 리디렉션 테스트의 핵심 로직을 구현한다.
-   **목표 5**: `README.md`에 사용자가 프로젝트를 실행하고 기본 테스트를 수행할 수 있는 최소한의 가이드를 포함한다.

## 3. 스프린트 백로그

-   **Story 1.1**: Docker Compose 기반 HA 인프라 구성
    -   Task 1.1.1: `docker-compose.ha.yml` 파일 생성
    -   Task 1.1.2: Valkey Master, Replica 2개 서비스 정의
    -   Task 1.1.3: Valkey Sentinel 3개 서비스 정의 및 `sentinel.conf` 설정

-   **Story 2.1**: Docker Compose 기반 Cluster 인프라 구성
    -   Task 2.1.1: `docker-compose.cluster.yml` 파일 생성
    -   Task 2.1.2: Valkey 노드 6개(Primary 3, Replica 3) 서비스 정의
    -   Task 2.1.4: 클러스터 구성을 위한 초기화 스크립트(meet, add-slots) 작성 및 서비스에 연동

-   **Story 1.2**: Python HA 테스트 클라이언트 개발 (일부)
    -   Task 1.2.1: `app/requirements.txt`에 필요 라이브러리 추가
    -   Task 1.2.2: `app/lib/ha_client.py`에 Sentinel 기반 동적 연결 로직 구현
    -   Task 1.2.4: `app/ha_test.py`에서 HA 환경 연결 및 기본 CRUD 테스트 구현

-   **Story 2.2**: Python Cluster 테스트 클라이언트 개발 (일부)
    -   Task 2.2.2: `app/lib/cluster_client.py`에 Cluster 연결 로직 구현
    -   Task 2.2.3: `app/cluster_test.py`에서 Cluster 환경 연결 및 기본 CRUD 테스트 구현

-   **Story 3.1**: 최종 사용자 가이드 문서 작성 (초안)
    -   Task 3.1.1: `README.md` 파일 생성
    -   Task 3.1.3: HA 및 Cluster 환경 실행 방법 명시

## 4. Capacity 및 리소스

-   **개발자**: Gemini CLI
-   **Capacity**: 100% (스프린트 기간 동안 본 과제에 집중)

## 5. Definition of Done (DoD) - 완료 조건

-   [ ] **HA 환경**: `docker-compose -f docker-compose.ha.yml up` 명령으로 모든 컨테이너가 오류 없이 정상적으로 실행된다.
-   [ ] **Cluster 환경**: `docker-compose -f docker-compose.cluster.yml up` 명령으로 모든 컨테이너가 정상 실행되고, 클러스터가 자동으로 구성되어 `cluster info` 또는 `cluster nodes` 명령이 성공적으로 반환된다.
-   [ ] **HA 테스트**: `python app/ha_test.py` 실행 시 Sentinel을 통해 Master에 연결하여 기본적 데이터 쓰기/읽기가 성공한다.
-   [ ] **Cluster 테스트**: `python app/cluster_test.py` 실행 시 Cluster에 연결하여 기본적 데이터 쓰기/읽기가 성공한다.
-   [ ] **Failover 테스트**: `docker kill valkey-master` 실행 시, `ha_test.py`가 잠시 후 새로운 Master를 감지하고 테스트를 계속 진행할 수 있다. (완벽한 재시도 로직이 아니더라도 핵심 기능 확인)
-   [ ] **Redirect 테스트**: `cluster_test.py`에서 `redis-py-cluster` 클라이언트가 `MOVED` 리디렉션을 자동으로 처리하여 키 조회/저장이 성공한다.
-   [ ] **문서화**: `README.md`에 각 환경을 실행하는 `docker-compose` 명령어와 Python 테스트 스크립트 실행 명령어가 명시되어 있다.
-   **코드 품질**: 생성된 모든 코드(YAML, Python)는 프롬프트의 요구사항을 충족하며, 주석이나 변수명을 통해 의도가 명확히 드러나야 한다.
