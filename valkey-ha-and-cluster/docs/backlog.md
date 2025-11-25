# Valkey 테스트 환경 구축 백로그

## Epics

-   **Epic 1: Valkey 고가용성(HA) 환경 구축 및 검증**
    -   Master-Replica-Sentinel 구조를 Docker로 구현하고, 자동 장애 복구(Failover) 기능을 Python으로 테스트하는 환경을 구축한다.

-   **Epic 2: Valkey 클러스터(Cluster) 환경 구축 및 검증**
    -   Multi-Shard Cluster를 Docker로 구현하고, 데이터 분산 및 리디렉션, 샤드 장애 복구 기능을 Python으로 테스트하는 환경을 구축한다.

-   **Epic 3: 프로젝트 문서화 및 사용성 개선**
    -   개발된 테스트 환경을 누구나 쉽게 이해하고 사용할 수 있도록 명확한 문서와 실행 가이드를 작성한다.

---

## Stories & Tasks

### Epic 1: Valkey 고가용성(HA) 환경 구축 및 검증

-   **Story 1.1: Docker Compose 기반 HA 인프라 구성**
    -   **Task 1.1.1**: `docker-compose.ha.yml` 파일 생성
    -   **Task 1.1.2**: Valkey Master, Replica 2개 서비스 정의
    -   **Task 1.1.3**: Valkey Sentinel 3개 서비스 정의 및 `sentinel.conf` 설정
    -   **Task 1.1.4**: 각 서비스 간 네트워크 및 의존성 설정

-   **Story 1.2: Python HA 테스트 클라이언트 개발**
    -   **Task 1.2.1**: `app/requirements.txt`에 `redis`, `rich`, `backoff` 추가
    -   **Task 1.2.2**: `app/lib/ha_client.py`에 Sentinel을 통해 Master/Replica를 동적으로 찾는 클라이언트 로직 구현
    -   **Task 1.2.3**: `app/lib/util.py`에 결과 출력을 위한 유틸리티 함수 추가
    -   **Task 1.2.4**: `app/ha_test.py` 기본 구조 및 테스트 시나리오 골격 작성

-   **Story 1.3: HA 자동 장애 복구(Failover) 테스트 구현**
    -   **Task 1.3.1**: `ha_test.py`에 기본 CRUD (쓰기/읽기) 테스트 기능 구현
    -   **Task 1.3.2**: Master 노드 장애 주입 시나리오 구현 (`docker kill`)
    -   **Task 1.3.3**: `ha_client.py`에 `backoff` 라이브러리를 이용한 재시도 및 자동 재연결 로직 구현
    -   **Task 1.3.4**: Failover 후 새로운 Master를 통해 데이터 일관성을 검증하는 테스트 코드 작성

---

### Epic 2: Valkey 클러스터(Cluster) 환경 구축 및 검증

-   **Story 2.1: Docker Compose 기반 Cluster 인프라 구성**
    -   **Task 2.1.1**: `docker-compose.cluster.yml` 파일 생성
    -   **Task 2.1.2**: Valkey 노드 6개(Primary 3, Replica 3) 서비스 정의
    -   **Task 2.1.3**: 각 노드의 `valkey.conf`에 클러스터 활성화 설정 추가
    -   **Task 2.1.4**: 클러스터 구성을 위한 초기화 스크립트(meet, add-slots) 작성 및 서비스에 연동

-   **Story 2.2: Python Cluster 테스트 클라이언트 개발**
    -   **Task 2.2.1**: `app/requirements.txt`에 `redis-py-cluster` 추가
    -   **Task 2.2.2**: `app/lib/cluster_client.py`에 `redis-py-cluster`를 사용한 클라이언트 연결 로직 구현
    -   **Task 2.2.3**: `app/cluster_test.py` 기본 구조 및 테스트 시나리오 골격 작성

-   **Story 2.3: Cluster 데이터 분산 및 장애 복구 테스트 구현**
    -   **Task 2.3.1**: `cluster_test.py`에 여러 키를 저장하고 슬롯 기반으로 분산되는지 검증하는 코드 작성
    -   **Task 2.3.2**: `MOVED` 리디렉션이 클라이언트에서 자동으로 처리되는지 확인하는 테스트 구현
    -   **Task 2.3.3**: 각 Shard별 저장된 키의 개수를 집계하여 출력하는 기능 구현
    -   **Task 2.3.4**: Primary 노드 장애 주입 후 Replica가 Primary로 승격되고 서비스가 복구되는지 검증하는 코드 작성

---

### Epic 3: 프로젝트 문서화 및 사용성 개선

-   **Story 3.1: 최종 사용자 가이드 문서 작성**
    -   **Task 3.1.1**: `README.md` 파일 생성
    -   **Task 3.1.2**: 프로젝트 개요 및 목적 작성
    -   **Task 3.1.3**: HA 및 Cluster 환경 실행 방법, 테스트 스크립트 사용법 명시
    -   **Task 3.1.4**: 장애 주입 방법 및 테스트 결과 예시 추가

-   **Story 3.2: Agile 개발 산출물 정리**
    -   **Task 3.2.1**: `docs/prd.md`에 프로젝트 요구사항 명세 작성
    -   **Task 3.2.2**: `docs/sprint_plan.md`에 첫 번째 스프린트 계획 수립
    -   **Task 3.2.3**: `docs/progress.md` 및 `docs/retro.md` 템플릿 생성
