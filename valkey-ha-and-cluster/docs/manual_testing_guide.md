# Valkey HA 및 Cluster 수동 테스트 가이드

이 가이드는 사용자가 직접 Valkey HA(Sentinel) 및 Cluster 환경을 구동하고 테스트할 수 있도록 단계별 지침을 제공합니다.

## 사전 요구사항

- Docker 및 Docker Compose 설치
- Python 3.8+ 설치
- 기본적인 터미널 사용 지식

## 1. HA (Sentinel) 환경 테스트

### 1.1 환경 시작

```bash
cd /home/ubuntu/dev-proj/agile_vibe_test/valkey-ha-and-cluster
docker-compose -f docker-compose.ha.yml up -d
```

**확인 사항:**
- 6개의 컨테이너가 실행되어야 합니다:
  - `valkey-master` (마스터)
  - `valkey-replica1`, `valkey-replica2` (레플리카)
  - `valkey-sentinel1`, `valkey-sentinel2`, `valkey-sentinel3` (센티널)

```bash
docker ps | grep valkey
```

### 1.2 Sentinel 상태 확인

Sentinel이 마스터를 정상적으로 모니터링하는지 확인:

```bash
docker exec valkey-sentinel1 valkey-cli -p 26379 SENTINEL get-master-addr-by-name myvalkey
```

**예상 출력:**
```
172.23.0.X
6379
```

### 1.3 데이터 쓰기 및 복제 확인

#### 마스터에 데이터 쓰기:
```bash
docker exec valkey-master valkey-cli SET test_key "Hello Valkey"
```

#### 마스터에서 읽기:
```bash
docker exec valkey-master valkey-cli GET test_key
```

**예상 출력:** `"Hello Valkey"`

#### 레플리카에서 읽기 (복제 확인):
```bash
docker exec valkey-replica1 valkey-cli GET test_key
```

**예상 출력:** `"Hello Valkey"`

### 1.4 자동 Failover 테스트

#### 1단계: 현재 마스터 확인
```bash
docker exec valkey-sentinel1 valkey-cli -p 26379 SENTINEL get-master-addr-by-name myvalkey
```

현재 마스터 IP를 기록해 둡니다.

#### 2단계: 마스터 종료
```bash
docker kill valkey-master
```

#### 3단계: Failover 대기 (15-20초)
```bash
sleep 20
```

#### 4단계: 새 마스터 확인
```bash
docker exec valkey-sentinel1 valkey-cli -p 26379 SENTINEL get-master-addr-by-name myvalkey
```

**확인 사항:**
- 새 마스터 IP가 이전과 다르게 변경되어야 합니다
- 레플리카 중 하나가 마스터로 승격되었습니다

#### 5단계: 데이터 보존 확인
새 마스터에서 이전에 저장한 데이터를 확인:

```bash
# 새 마스터 IP 확인 후 (예: 172.23.0.6)
docker exec valkey-replica1 valkey-cli GET test_key
```

**예상 출력:** `"Hello Valkey"` (데이터가 보존되어야 함)

#### 6단계: Sentinel 로그 확인
```bash
docker logs valkey-sentinel1 --tail 50 | grep -E "(failover|promoted)"
```

**확인 사항:**
- `+promoted-slave` 메시지 확인
- `+failover-end` 메시지 확인

### 1.5 환경 정리

```bash
docker-compose -f docker-compose.ha.yml down
```

---

## 2. Cluster 환경 테스트

### 2.1 환경 시작

```bash
cd /home/ubuntu/dev-proj/agile_vibe_test/valkey-ha-and-cluster
docker-compose -f docker-compose.cluster.yml up -d
```

**확인 사항:**
- 7개의 컨테이너가 실행되어야 합니다:
  - `node-7000` ~ `node-7005` (6개 노드)
  - `cluster-initializer` (초기화 스크립트, 완료 후 종료됨)

```bash
docker ps | grep node
```

### 2.2 클러스터 초기화 대기

초기화 스크립트가 완료될 때까지 대기 (약 10-15초):

```bash
sleep 15
```

### 2.3 클러스터 상태 확인

```bash
docker exec node-7000 valkey-cli -p 6379 CLUSTER INFO
```

**확인 사항:**
- `cluster_state:ok` 표시
- `cluster_slots_assigned:16384` 표시

### 2.4 클러스터 노드 확인

```bash
docker exec node-7000 valkey-cli -p 6379 CLUSTER NODES
```

**확인 사항:**
- 3개의 마스터 노드 (master 표시)
- 3개의 레플리카 노드 (slave 표시)
- 각 마스터는 슬롯 범위를 할당받아야 함

### 2.5 데이터 분산 테스트

여러 키를 저장하여 클러스터 전체에 분산되는지 확인:

```bash
# 여러 키 저장
for i in {0..9}; do
  docker exec node-7000 valkey-cli -p 6379 SET "key-$i" "value-$i"
done
```

### 2.6 리디렉션 확인

특정 노드에서 다른 노드의 키를 조회하면 자동 리디렉션이 발생:

```bash
# node-7001에서 모든 키 조회 시도
for i in {0..9}; do
  echo "Getting key-$i:"
  docker exec node-7001 valkey-cli -p 6379 GET "key-$i"
done
```

**확인 사항:**
- 모든 키가 정상적으로 조회되어야 함 (리디렉션 자동 처리)

### 2.7 키 분포 확인

각 노드에 저장된 키 개수 확인:

```bash
echo "Node 7000:"
docker exec node-7000 valkey-cli -p 6379 DBSIZE

echo "Node 7001:"
docker exec node-7001 valkey-cli -p 6379 DBSIZE

echo "Node 7002:"
docker exec node-7002 valkey-cli -p 6379 DBSIZE
```

**확인 사항:**
- 키가 여러 노드에 분산되어 저장되어야 함

### 2.8 자동 Failover 테스트

#### 1단계: 마스터 노드 확인
```bash
docker exec node-7000 valkey-cli -p 6379 CLUSTER NODES | grep master
```
임의의 마스터 노드 ID와 IP를 확인합니다 (예: `node-7000`).

#### 2단계: 마스터 노드 종료
```bash
docker kill valkey-ha-and-cluster-node-7000-1
```
*주의: 컨테이너 이름은 `docker ps`로 확인 필요할 수 있음*

#### 3단계: Failover 대기 (약 15-30초)
```bash
sleep 30
```

#### 4단계: 클러스터 상태 확인 (다른 노드에서)
```bash
docker exec node-7001 valkey-cli -p 6379 CLUSTER NODES
```

**확인 사항:**
- 종료된 노드가 `fail` 상태로 표시됨
- 해당 노드의 레플리카가 새로운 마스터(`master`)로 승격됨

### 2.9 환경 정리

```bash
docker-compose -f docker-compose.cluster.yml down
```

---

## 3. Python 테스트 스크립트 실행 (선택 사항)

자동화된 테스트 스크립트를 실행하려면:

### 3.1 HA 테스트

```bash
# HA 환경 시작
docker-compose -f docker-compose.ha.yml up -d

# 테스트 실행
sleep 5
docker-compose -f docker-compose.ha.yml --profile test run --rm ha-test-client

# 환경 정리
docker-compose -f docker-compose.ha.yml down
```

### 3.2 Cluster 테스트

```bash
# Cluster 환경 시작
docker-compose -f docker-compose.cluster.yml up -d

# 초기화 대기
sleep 15

# 테스트 실행
# 이 스크립트는 다음 항목을 자동으로 검증합니다:
# 1. 클러스터 연결
# 2. 키 분산 및 리디렉션
# 3. 키 분산 통계 (노드별 키 개수)
# 4. 자동 Failover (노드 장애 시 복구)
docker-compose -f docker-compose.cluster.yml --profile test run --rm cluster-test-client

# 환경 정리
docker-compose -f docker-compose.cluster.yml down
```

---

## 4. 문제 해결

### 컨테이너가 시작되지 않는 경우

```bash
# 로그 확인
docker logs <container-name>

# 예: docker logs valkey-master
```

### 포트 충돌 발생 시

기존에 실행 중인 컨테이너 정리:

```bash
docker-compose -f docker-compose.ha.yml down
docker-compose -f docker-compose.cluster.yml down
```

### Sentinel이 마스터를 찾지 못하는 경우

Sentinel 재시작:

```bash
docker-compose -f docker-compose.ha.yml restart valkey-sentinel1 valkey-sentinel2 valkey-sentinel3
sleep 5
```

---

## 5. 추가 명령어

### 모든 Valkey 컨테이너 확인
```bash
docker ps -a | grep valkey
```

### 특정 컨테이너 로그 실시간 확인
```bash
docker logs -f <container-name>
```

### 컨테이너 내부 접속
```bash
docker exec -it <container-name> sh
```

### Valkey CLI 직접 사용
```bash
docker exec -it valkey-master valkey-cli
```

---

## 6. 테스트 체크리스트

### HA 환경
- [ ] 6개 컨테이너 정상 실행 확인
- [ ] Sentinel이 마스터 주소 반환 확인
- [ ] 마스터에 데이터 쓰기 성공
- [ ] 레플리카에서 데이터 읽기 성공 (복제 확인)
- [ ] 마스터 종료 후 Failover 발생 확인
- [ ] 새 마스터에서 데이터 보존 확인

### Cluster 환경
- [ ] 7개 컨테이너 정상 실행 확인
- [ ] 클러스터 상태 `ok` 확인
- [ ] 16384개 슬롯 모두 할당 확인
- [ ] 3개 마스터, 3개 레플리카 확인
- [ ] 데이터 분산 저장 확인
- [ ] 리디렉션 자동 처리 확인
- [ ] 키 분산 통계 확인 (Python 스크립트)
- [ ] 키 분산 통계 확인 (Python 스크립트)
- [ ] 자동 Failover 및 복구 확인 (수동 및 Python 스크립트)
