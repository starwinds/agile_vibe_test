# Valkey 고가용성(HA) 및 클러스터 테스트 환경 구축

## 1. 프로젝트 개요

본 프로젝트는 Valkey의 두 가지 핵심적인 고가용성 및 분산 아키텍처인 **Master-Replica-Sentinel (HA)** 구조와 **Cluster** 구조를 Docker Compose 환경에 구축하고, 각 아키텍처의 안정성과 기능을 검증하기 위한 Python 기반 자동화 테스트 스위트를 개발하는 것을 목표로 합니다.

이를 통해 개발자들은 실제 운영 환경과 유사한 테스트베드에서 Valkey의 Auto-Failover, Sharding, Redirection 등의 핵심 기능을 신속하게 검증하고 이해할 수 있습니다.

## 2. 프로젝트 목표

- **자동화된 테스트 환경 구축**: Docker Compose를 사용하여 클릭 한 번으로 Valkey HA 및 Cluster 환경을 신속하게 구성합니다.
- **Python 기반 기능 검증**: Python 테스트 스크립트를 통해 각 아키텍처의 핵심 기능(장애 복구, 데이터 분산 등)이 정상적으로 동작하는지 자동으로 검증합니다.
- **안정적인 장애 시나리오 테스트**: Master 노드 또는 Primary Shard 장애 상황을 시뮬레이션하고, 시스템이 예상대로 자동 복구되는지 확인합니다.
- **명확한 개발 및 사용 가이드 제공**: `README.md` 문서를 통해 누구나 쉽게 테스트 환경을 구성하고 실행할 수 있도록 안내합니다.

## 3. 사용자 시나리오

### 시나리오 1: HA 구조의 자동 장애 복구(Auto-Failover) 검증

1.  **개발자**는 `docker-compose.ha.yml`을 실행하여 Master-Replica-Sentinel 환경을 구축합니다.
2.  `ha_test.py` 스크립트를 실행하여 초기 데이터 CRUD가 정상적으로 Master 노드에 기록되는 것을 확인합니다.
3.  테스트 스크립트가 실행되는 동안 `docker kill` 명령으로 `valkey-master` 컨테이너를 강제 종료하여 장애 상황을 시뮬레이션합니다.
4.  Sentinel이 장애를 감지하고 Replica 중 하나를 새로운 Master로 승격시키는 과정을 관찰합니다.
5.  Python 클라이언트는 Sentinel을 통해 새로운 Master 정보를 자동으로 받아오고, 중단되었던 CRUD 작업을 재개하여 데이터 일관성을 검증합니다.

### 시나리오 2: Cluster 구조의 데이터 분산 및 리디렉션 검증

1.  **개발자**는 `docker-compose.cluster.yml`을 실행하여 3개의 Primary와 3개의 Replica로 구성된 Valkey Cluster를 구축합니다.
2.  `cluster_test.py` 스크립트를 실행하여 여러 개의 키-값 데이터를 Cluster에 저장합니다.
3.  스크립트는 각 키가 해시 슬롯(hash slot)에 따라 올바른 Shard에 분산 저장되었는지 확인하고, Shard별 키 개수를 출력합니다.
4.  특정 키 조회 시 다른 Shard로 접근했을 때 발생하는 `MOVED` 리디렉션이 클라이언트 라이브러리에 의해 자동으로 처리되는지 검증합니다.
5.  Primary Shard 하나를 `docker kill`로 종료시킨 후, 해당 Shard의 Replica가 새로운 Primary로 승격되고 클러스터가 정상적으로 서비스를 재개하는지 확인합니다.

## 4. 핵심 기능 정의

### 기능 1: Valkey HA (Master-Replica-Sentinel) 환경 구성
- **구성 요소**: Master 1개, Replica 2개, Sentinel 3개로 구성된 Docker Compose 파일 (`docker-compose.ha.yml`)
- **자동화**: Replica는 Master에 자동으로 복제를 시작해야 합니다.
- **Sentinel 설정**: `mymaster` 그룹을 모니터링하며, 2초 내 응답이 없으면 다운으로 간주하고 10초 내에 failover를 완료하도록 설정합니다.

### 기능 2: Valkey Cluster 환경 구성
- **구성 요소**: Primary 3개, Replica 3개로 구성된 Docker Compose 파일 (`docker-compose.cluster.yml`)
- **자동화**: Cluster 구성을 위한 `cluster meet` 및 슬롯 할당(`slot assign`) 과정이 스크립트로 자동화되어야 합니다.
- **설정**: `cluster-enabled yes` 및 `cluster-require-full-coverage no` 옵션을 적용합니다.

### 기능 3: Python HA 테스트 스크립트 (`ha_test.py`)
- **연결**: Sentinel을 통해 현재 Master 노드의 주소를 동적으로 조회합니다.
- **장애 복구 테스트**: Master 노드 장애 시, `backoff` 또는 `retrying` 라이브러리를 사용하여 재연결을 시도하고 새로운 Master를 찾아 작업을 재개하는 로직을 포함합니다.
- **데이터 일관성 검증**: Failover 전후에 동일한 키에 대한 데이터가 일관되게 유지되는지 확인합니다.

### 기능 4: Python Cluster 테스트 스크립트 (`cluster_test.py`)
- **연결**: `redis-py-cluster` 라이브러리를 사용하여 Cluster 노드에 연결합니다.
- **데이터 분산 검증**: 여러 키를 저장한 후, 각 키가 어느 슬롯과 Shard에 저장되었는지 확인하고 통계를 출력합니다.
- **리디렉션 처리**: `MOVED` 및 `ASK` 리디렉션이 클라이언트 단에서 투명하게 처리되는지 검증합니다.
- **장애 복구 테스트**: Primary Shard 장애 시 Replica가 승격되고, 클러스터가 정상 상태로 복구되는지 확인합니다.

### 기능 5: 문서화 (`README.md`)
- 각 환경(HA, Cluster)의 실행 방법, 테스트 스크립트 사용법, 장애 주입 명령어 예시를 명확하게 기술합니다.
- 테스트 결과 출력 예시와 그 의미를 설명하여 사용자의 이해를 돕습니다.
