
# Gemini CLI Prompt  
## Valkey HA(Master–Replica–Sentinel) + Valkey Cluster 구성 & Python 테스트 앱 자동 생성

이 문서는 **Gemini CLI에게 직접 전달하는 개발 과제 프롬프트**입니다.  
Valkey의 고가용성 구조(HA)와 Cluster 구조를 Docker Compose 기반으로 구성하고,  
각 구조를 Python 앱으로 테스트하기 위한 전체 개발 과제를 자동 생성하도록 지시합니다.

---

# ⭐ 역할 정의

너는 Valkey 기반 고가용성 구조 테스트 환경을 구축하는  
**Backend Infrastructure Engineer + Python Developer + Docker Compose Architect** 이다.

목표는 다음 두 가지 Valkey 구성을 만들고, 각각의 기능을 Python 테스트 앱으로 자동 검증하는 환경을 구현하는 것이다.

1) Valkey **Master–Replica–Sentinel(HA) 구조**  
2) Valkey **Cluster (3 Shards × Replica 1 = 6 nodes)** 구조  

모든 구현물은 Docker Compose + Python 테스트 앱 기반이어야 한다.

---

# 🎯 1. 개발 과제 목표

## A. Valkey HA 구조 (Sentinel 기반 Auto-Failover)
- master 1개 + replica 2개 + sentinel 3개
- failover 발생 시 sentinel이 새로운 master 선출
- Python 앱에서 failover 자동 인지 및 정상 동작 확인
- sentinel → 새로운 master 주소 발견 가능해야 함

## B. Valkey Cluster 구조 (Slot 기반 Routing)
- primary 3개 (7000, 7001, 7002)
- replica 3개 (7003, 7004, 7005)
- slot 자동 분배
- MOVED / ASK redirect 정상 처리
- 특정 shard 장애 후 replica 승격 테스트

## C. Python 테스트 자동화
각 구조를 대상으로 다음 수행:

### HA 테스트
1. 기본 CRUD
2. master kill 후 failover 테스트
3. sentinel을 통한 새로운 master 발견
4. reconnect 및 재시도(backoff) 로직 정상 동작 확인
5. failover 후 key 일관성 체크

### Cluster 테스트
1. Slot 기반 key 배치 테스트
2. MOVED/ASK 자동 처리 확인
3. key 분산 상태 출력(shard별 key count)
4. 특정 shard 장애 후 replica 승격 및 복구 검증

---

# 📁 2. 디렉토리 구조 요구사항

작업 디렉토리는 아래 경로에 생성되어 있음

- /home/ubuntu/dev-proj/agile_vibe_test/valkey-ha-and-cluster

- 위 경로의 디렉토리 활용하고, 디렉토리를 중복 생성하면 안됨

```
valkey-ha-and-cluster/
 ├─ docker-compose.ha.yml
 ├─ docker-compose.cluster.yml
 ├─ app/
 │   ├─ ha_test.py
 │   ├─ cluster_test.py
 │   ├─ lib/
 │   │   ├─ ha_client.py
 │   │   ├─ cluster_client.py
 │   │   └─ util.py
 │   └─ requirements.txt
 └─ README.md
```

---

# 🧱 3. Docker Compose 구성 상세 요구사항

## A. docker-compose.ha.yml (Master–Replica–Sentinel)

### 구성 조건
- master 1개: `valkey-master`
- replica 2개: `valkey-replica1`, `valkey-replica2`
- sentinel 3개: `valkey-sentinel1`, `valkey-sentinel2`, `valkey-sentinel3`
- replica들은 자동 REPLICAOF
- sentinel 설정:

```
sentinel monitor myvalkey valkey-master 6379 2
sentinel down-after-milliseconds myvalkey 2000
sentinel failover-timeout myvalkey 10000
```

### 테스트 편의 요구
- master container 이름은 반드시 `valkey-master`
- 장애 주입을 위해 kill 테스트 용이해야 함
- sentinel 로그 확인 가능해야 함

---

## B. docker-compose.cluster.yml (Cluster 구조)

### 구성 조건
- 총 6개 노드  
  primary: node-7000, node-7001, node-7002  
  replica: node-7003, node-7004, node-7005
- 각 노드 포트: 7000~7005
- cluster-enabled yes
- cluster-config-file 자동 생성
- cluster-require-full-coverage no
- replicas 자동 배치 스크립트 포함
- cluster meet / slot assign 자동화 스크립트 포함

---

# 🧪 4. Python 테스트 앱 요구사항

## 공통 사항
- requirements.txt에 포함:
  - redis
  - redis-py-cluster
  - rich
  - backoff 또는 retrying
- 모든 테스트는 결과 dict 또는 rich 테이블 형태 출력

---

## A. HA 테스트 (`ha_test.py`)

### Sentinel 연결
```
sentinel = redis.sentinel.Sentinel(
    [("valkey-sentinel1", 26379), ("valkey-sentinel2", 26379), ("valkey-sentinel3", 26379)]
)
master = sentinel.discover_master("myvalkey")
```

### 테스트 시나리오
1. CRUD 테스트  
2. master kill 테스트 (`docker kill valkey-master`)  
3. retry → 새로운 master 검출  
4. failover 후 GET key 정상 반환  
5. replica sync 상태 확인  

---

## B. Cluster 테스트 (`cluster_test.py`)

1. cluster client 연결
2. slot 기반 key 분배 테스트
3. MOVED/ASK 자동 처리 확인
4. shard별 key count 출력
5. 특정 primary kill → replica 승격 → 자동 복구 확인

---

# 📝 5. README.md 구성

- HA 실행:
```
docker-compose -f docker-compose.ha.yml up -d
python app/ha_test.py
```

- Cluster 실행:
```
docker-compose -f docker-compose.cluster.yml up -d
python app/cluster_test.py
```

- 장애 주입 방법:
```
docker kill valkey-master
docker kill node-7000
```

- 출력 예시 및 결과 해석 포함

---

# 📜 6. Gemini CLI의 출력 형식 (반드시 아래 형식 준수)

```
--- 파일: docker-compose.ha.yml ---
```yaml
# (전체 코드)

--- 파일: docker-compose.cluster.yml ---
```yaml
# (전체 코드)

--- 파일: app/ha_test.py ---
```python
# (전체 코드)

--- 파일: app/cluster_test.py ---
```python
# (전체 코드)

--- 파일: app/lib/ha_client.py ---
```python
# (전체 코드)

--- 파일: app/lib/cluster_client.py ---
```python
# (전체 코드)

--- 파일: app/lib/util.py ---
```python
# (전체 코드)

--- 파일: app/requirements.txt ---
```txt
# (전체 내용)

--- 파일: README.md ---
```markdown
# (전체 내용)
```

### 출력 누락 금지  
### 파일명·전체코드 반드시 포함  

---

# 🏁 7. 개발 진행 방식

Agile 개발 방식으로 인간과 협업 진행
아래의 Agile 문서 생성 기준을 충족

### docs/prd.md
- 프로젝트 개요, 목표, 사용자 시나리오, 기능 정의

### docs/backlog.md
- Epic/Story/Task 기반 정의

### docs/sprint_plan.md
- Sprint 1 기간, 목표, Capacity, Definition of Done 포함
- 완료 조건(DoD)
  . HA 및 Cluster compose 모두 정상 실행
  . Python 테스트 앱 정상 실행
  . Failover / Cluster Redirect 테스트 정상 통과
  . README에 전체 사용법 포함
  . 코드 구조·동작 문제 없음


### docs/progress.md
- 날짜 / 작업 / 테스트 결과 / 커버리지 정리

### docs/retro.md
- 잘된 점 / 개선점 / 다음 스프린트 액션 아이템

코드 생산 방식은 TDD 방법론에 따라 진행
아래 경로의 개발 가이드 문서 참조

### 개발 가이드 문서
- 아래 경로의 가이드 문서 참조

/home/ubuntu/dev-proj/agile_vibe_test/dev_guide.txt


---

# 🔚 이 전체 프롬프트 내용을 정확히 반영하여 개발을 시작하라.
