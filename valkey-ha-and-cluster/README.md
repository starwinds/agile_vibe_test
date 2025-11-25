# Valkey HA 및 클러스터 테스트 환경

이 프로젝트는 Docker Compose와 Python을 사용하여 Valkey의 고가용성(HA) 및 클러스터 기능을 테스트하고 시연하기 위한 완전 자동화된 환경을 제공합니다.

## 1. 프로젝트 목표

이 프로젝트의 주요 목표는 Valkey의 두 가지 핵심 아키텍처를 직접 체험할 수 있는 간단한 테스트 환경을 제공하는 것입니다.

1.  **Valkey HA (Master-Replica-Sentinel)**: 마스터 노드가 다운되었을 때 자동 장애 조치(failover)를 시연합니다.
2.  **Valkey 클러스터**: 데이터 샤딩, 리디렉션 (`MOVED`/`ASK`), 그리고 프라이머리 샤드의 장애 조치를 시연합니다.

## 2. 디렉토리 구조

```
valkey-ha-and-cluster/
 ├─ docker-compose.ha.yml        # HA 설정을 위한 Docker Compose
 ├─ docker-compose.cluster.yml   # 클러스터 설정을 위한 Docker Compose
 ├─ config/                      # Valkey 설정 파일
 │   ├─ sentinel.conf
 │   ├─ valkey-cluster.conf
 │   └─ cluster-init.sh
 ├─ app/                         # Python 테스트 애플리케이션
 │   ├─ ha_test.py               # HA 테스트 스크립트
 │   ├─ cluster_test.py          # 클러스터 테스트 스크립트
 │   ├─ lib/                     # 클라이언트 라이브러리
 │   │   ├─ ha_client.py
 │   │   ├─ cluster_client.py
 │   │   └─ util.py
 │   └─ requirements.txt         # Python 의존성
 └─ README.md                    # 이 파일
```

## 3. 사전 요구사항

-   Docker & Docker Compose
-   Python 3.8+
-   의존성 설치를 위한 `pip`

## 4. 실행 방법

### A. Valkey HA (Sentinel) 테스트

이 테스트는 자동 장애 조치를 시연합니다.

#### 1단계: HA 환경 시작

`valkey-ha-and-cluster` 디렉토리에서 다음을 실행합니다:
```bash
docker-compose -f docker-compose.ha.yml up -d
```
이 명령은 다음을 시작합니다:
- `valkey-master` (마스터)
- `valkey-replica1`, `valkey-replica2` (복제본)
- `valkey-sentinel1`, `valkey-sentinel2`, `valkey-sentinel3` (센티널)

#### 2단계: Python 환경 설정

`app` 디렉토리로 이동하여 의존성을 설치합니다. 가상 환경 사용을 권장합니다.
```bash
cd app
python -m venv .venv
source .venv/bin/activate  # Windows의 경우: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 3단계: HA 테스트 실행

테스트 스크립트는 CRUD 작업을 수행한 다음 마스터 장애를 시뮬레이션하고 시스템이 복구되는지 확인합니다.

```bash
python ha_test.py
```

**테스트 중 수동으로 장애를 주입할 수 있습니다:**
```bash
docker kill valkey-master
```
Python 스크립트는 Sentinel을 통해 새 마스터를 자동으로 감지하고 작업을 계속합니다.

### B. Valkey 클러스터 테스트

이 테스트는 데이터 샤딩 및 클러스터 장애 조치를 시연합니다.

#### 1단계: 클러스터 환경 시작

`valkey-ha-and-cluster` 디렉토리에서 다음을 실행합니다:
```bash
docker-compose -f docker-compose.cluster.yml up -d
```
이 명령은 6개의 Valkey 노드와 클러스터(프라이머리 3개, 복제본 3개)를 자동으로 구성하는 초기화 스크립트를 시작합니다.

#### 2단계: 클러스터 테스트 실행

Python 환경을 이미 설정했다면 `app` 디렉토리에서 테스트 스크립트를 직접 실행할 수 있습니다.
```bash
python cluster_test.py
```
스크립트는 클러스터 전체에 키를 분산시키고 리디렉션이 작동하는지 확인한 다음 프라이머리 노드 장애를 시뮬레이션하여 복제본 승격을 테스트합니다.

**테스트 중 수동으로 장애를 주입하려면:**
```bash
# 스크립트가 어떤 컨테이너를 종료할지 알려주지만, 보통 다음 중 하나입니다
docker kill node-7000
# 또는
docker kill node-7001
# 또는
docker kill node-7002
```

## 5. 결과 해석

테스트 스크립트는 `rich` 라이브러리를 사용하여 명확하고 색상으로 구분된 출력을 제공합니다.

-   **[yellow]▶ 단계...[/yellow]**: 현재 테스트 단계를 나타냅니다.
-   **[green]✅ 성공[/green]**: 단계가 성공적으로 완료되었습니다.
-   **[bold red]❌ 실패[/bold red]**: 단계가 실패했습니다.
-   **[blue]ℹ️ 정보[/blue]**: 현재 활성 마스터 또는 종료할 컨테이너와 같은 정보 메시지를 제공합니다.

### HA 테스트 출력 예시

```
▶ HAClient 초기화 중...
▶ Sentinel을 사용하여 마스터 및 복제본 검색 중...
✅ 검색된 마스터: 172.23.0.2:6379
✅ 검색된 복제본: 172.23.0.3:6379

===== 1단계: 기본 CRUD 작업 =====

▶ 마스터에 'ha_test_key'를 'hello_ha'로 설정 중...
✅ 'ha_test_key'를 성공적으로 설정했습니다.
▶ 마스터에서 'ha_test_key' 가져오는 중...
✅ 마스터에서 'hello_ha' 값을 가져왔습니다.
...

===== 2단계: 자동 장애 조치 테스트 =====

ℹ️ 현재 마스터는 172.23.0.2:6379 입니다.
▶ 컨테이너를 종료하여 마스터 장애 시뮬레이션 중...
✅ `docker kill valkey-master` 명령이 실행되었습니다.
...
▶ 장애 조치 후 값 가져오기 시도 중...
▶ Sentinel을 사용하여 마스터 및 복제본 검색 중...
✅ 검색된 마스터: 172.23.0.4:6379
✅ 검색된 복제본: 172.23.0.3:6379
✅ 새 마스터에서 'hello_ha'를 성공적으로 읽었습니다.
ℹ️ 장애 조치 성공. 새 마스터는 172.23.0.4:6379 입니다.
```

### 클러스터 테스트 출력 예시
```
===== 1단계: 키 분산 및 리디렉션 테스트 =====

▶ 분산을 관찰하기 위해 20개의 키 설정 중...
...
▶ 리디렉션을 테스트하기 위해 몇 개의 키 가져오는 중...
✅ 'key-5'에 대한 값 'value-5'를 가져왔습니다.
✅ 'key-15'에 대한 값 'value-15'를 가져왔습니다.

... (키 분산 테이블) ...

===== 2단계: 클러스터 장애 조치 테스트 =====

ℹ️ 'key-0' 키는 포트 7000의 노드에 있습니다. 장애 시뮬레이션을 위해 컨테이너 node-7000을 대상으로 합니다.
▶ 컨테이너 node-7000 종료 중...
✅ `docker kill node-7000`이 실행되었습니다.
...
▶ 장애 조치 후 'key-0' 가져오기 시도 중...
✅ 장애 조치 후 'key-0'을 성공적으로 검색했습니다. 클러스터가 복구되었습니다.
```