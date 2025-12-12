# Valkey Vector Benchmark 진행 내역 요약

## 📋 프로젝트 개요

VectorDBBench 프레임워크에 Valkey Vector Search 기능을 벤치마크할 수 있는 백엔드 클라이언트를 추가하는 프로젝트입니다.

---

## ✅ 완료된 작업

### 1. 핵심 구현 파일

#### ✅ `vectordb_bench/backend/clients/valkey/config.py`
- **ValkeyDBConfig**: 데이터베이스 연결 설정 클래스
  - Standalone, Cluster, Sentinel 배포 타입 지원
  - 호스트, 포트, 비밀번호, 노드 목록, 서비스 이름 설정
- **ValkeyDBCaseConfig**: 벤치마크 케이스별 설정 클래스
  - HNSW 파라미터: M, EF_CONSTRUCTION, EF_RUNTIME
  - 거리 메트릭: COSINE, L2 지원
  - 인덱스 이름, 프리픽스 설정

#### ✅ `vectordb_bench/backend/clients/valkey/new_client.py`
- **ValkeyClient**: VectorDB 추상 클래스 구현
  - **주요 기능**:
    - `_init_index()`: FT.CREATE를 사용한 HNSW 인덱스 생성
    - `insert_embeddings()`: Pipeline 기반 대량 데이터 삽입
    - `search_embedding()`: KNN 벡터 검색 (필터 지원)
    - `cleanup()`: 인덱스 및 문서 삭제
  - **배포 타입 지원**:
    - Standalone: 단일 노드 연결
    - Cluster: ValkeyCluster 클라이언트 사용
    - Sentinel: Sentinel을 통한 Master 연결

#### ✅ `vectordb_bench/backend/clients/valkey/cli.py`
- CLI 명령어 지원 (`vectordbbench valkey`)
- 배포 타입, 노드 목록, HNSW 파라미터 등을 CLI 옵션으로 지원

#### ✅ `vectordb_bench/backend/clients/__init__.py`
- DB enum에 Valkey 등록 완료
- 클라이언트 및 설정 클래스 매핑 완료

### 2. 테스트 코드

#### ✅ `tests/test_valkey_client.py`
- 단위 테스트 구현:
  - 인덱스 생성 테스트
  - 데이터 삽입 테스트
  - 검색 기능 테스트
  - Cleanup 기능 테스트

### 3. 설정 파일 및 문서

#### ✅ `valkey_bench_config.yaml`
- 벤치마크 실행용 설정 파일
- 현재 활성화된 케이스: `case_id: 3` (Cluster 모드)
- 주석 처리된 케이스:
  - `case_id: 1`: Standalone HNSW
  - `case_id: 2`: Standalone FLAT
  - `case_id: 3`: Cluster HNSW (현재 활성화)

#### ✅ 문서화
- `docs/manual_benchmark_guide.md`: 수동 벤치마크 가이드
- `docs/valkey_hnsw_tuning.md`: HNSW 파라미터 튜닝 가이드
- `docs/valkey_bench_result_summary.md`: 벤치마크 결과 요약 (실패 원인 분석 포함)
- `vectordb_bench/backend/clients/valkey/README.md`: 클라이언트 사용법

### 4. Docker 환경 설정

#### ✅ `docker-compose.benchmark-cluster.yml`
- 6개 노드 클러스터 구성 (포트 7000-7005)
- 클러스터 초기화 스크립트 포함

#### ✅ `docker-compose.benchmark-ha.yml`
- HA(Sentinel) 환경 구성 파일 존재

#### ✅ `config/` 디렉토리
- `valkey-cluster.conf`: 클러스터 설정 파일
- `cluster-init.sh`: 클러스터 초기화 스크립트
- `sentinel.conf`: Sentinel 설정 파일
- `sentinel-entrypoint.sh`: Sentinel 엔트리포인트 스크립트

---

## ⚠️ 현재 상태 및 문제점

### 벤치마크 테스트 중단 상태

#### 1. Cluster 모드 실패
- **에러**: `TimeoutError: Timeout connecting to server`
- **원인**: 
  - 클러스터 노드에 연결할 수 없음
  - `valkey_bench_config.yaml`에서 노드가 `['127.0.0.1:7000']` 하나만 설정됨 (실제로는 6개 노드 필요)
  - Docker 컨테이너가 실행 중이지 않았을 가능성
- **로그 파일**: `final_cluster_benchmark.log`

#### 2. Standalone 모드 실패
- **에러**: `ConnectionRefusedError: [Errno 111] Connection refused`
- **원인**: 
  - Valkey 서버가 실행 중이지 않음
  - 포트 6379에 연결할 수 없음
- **로그 파일**: `standalone_final_test.log`

#### 3. HA (Sentinel) 모드 실패 (문서에 언급됨)
- **에러**: `ConnectionError: Error while reading from 127.0.0.1:26379 : (104, 'Connection reset by peer')`
- **원인**: 
  - Sentinel 연결 문제
  - 네트워크 설정 이슈 가능성

### 알려진 이슈

1. **설정 파일 불일치**:
   - `valkey_bench_config.yaml`의 Cluster 케이스에 노드가 1개만 설정되어 있음
   - 실제 클러스터는 6개 노드 필요

2. **Docker 컨테이너 상태 불명확**:
   - 벤치마크 실행 시 컨테이너가 실행 중인지 확인 필요

3. **타입 불일치 문제 (해결됨)**:
   - `db_config`가 dict로 전달되는 경우 처리 로직 추가됨
   - `new_client.py`에서 dict/object 모두 처리 가능하도록 구현됨

---

## 📝 벤치마크 실행 방법

### Standalone 모드

1. **Valkey 서버 실행**:
   ```bash
   docker run -d --name valkey-vector-bench -p 6379:6379 valkey/valkey-bundle:latest
   ```

2. **설정 파일 수정** (`valkey_bench_config.yaml`):
   - `case_id: 1` 또는 `case_id: 2` 활성화
   - 다른 케이스 주석 처리

3. **벤치마크 실행**:
   ```bash
   cd VectorDBBench
   vectordbbench test --config-file valkey_bench_config.yaml
   ```

### Cluster 모드

1. **클러스터 실행**:
   ```bash
   docker-compose -f docker-compose.benchmark-cluster.yml up -d
   
   # 초기화 완료 대기
   docker logs -f cluster-initializer
   # ">>> Valkey Cluster initialized." 메시지 확인 후 Ctrl+C
   ```

2. **설정 파일 수정** (`valkey_bench_config.yaml`):
   - `case_id: 3` 활성화 (현재 활성화됨)
   - **중요**: `nodes` 리스트에 모든 노드 추가:
     ```yaml
     nodes:
       - "127.0.0.1:7000"
       - "127.0.0.1:7001"
       - "127.0.0.1:7002"
       - "127.0.0.1:7003"
       - "127.0.0.1:7004"
       - "127.0.0.1:7005"
     ```

3. **벤치마크 실행**:
   ```bash
   vectordbbench test --config-file valkey_bench_config.yaml
   ```

### HA (Sentinel) 모드

1. **HA 환경 실행**:
   ```bash
   docker-compose -f docker-compose.benchmark-ha.yml up -d
   ```

2. **설정 파일 수정** (`valkey_bench_config.yaml`):
   - `case_id: 4` 활성화 (현재 없음, 추가 필요)
   - `deployment_type: SENTINEL` 설정
   - `service_name` 설정

---

## 🔧 다음 단계 권장 사항

### 즉시 해결 필요

1. **설정 파일 수정**:
   - `valkey_bench_config.yaml`의 Cluster 케이스에 모든 노드 추가
   - HA 케이스 추가 (필요시)

2. **Docker 컨테이너 상태 확인**:
   ```bash
   docker ps -a
   docker-compose -f docker-compose.benchmark-cluster.yml ps
   ```

3. **네트워크 연결 테스트**:
   ```bash
   # Standalone
   redis-cli -h 127.0.0.1 -p 6379 ping
   
   # Cluster
   redis-cli -h 127.0.0.1 -p 7000 cluster nodes
   ```

### 개선 사항

1. **에러 처리 강화**:
   - 연결 실패 시 더 명확한 에러 메시지
   - 재시도 로직 추가

2. **설정 검증**:
   - 벤치마크 시작 전 설정 파일 유효성 검사
   - 필수 서비스 실행 여부 확인

3. **문서 보완**:
   - 트러블슈팅 가이드 추가
   - 각 배포 타입별 상세 실행 가이드

---

## 📊 구현 완료도

| 항목 | 상태 | 비고 |
|------|------|------|
| 핵심 클라이언트 구현 | ✅ 완료 | Standalone/Cluster/Sentinel 지원 |
| 설정 클래스 | ✅ 완료 | DBConfig, DBCaseConfig 구현 |
| CLI 지원 | ✅ 완료 | `vectordbbench valkey` 명령어 |
| 단위 테스트 | ✅ 완료 | 기본 테스트 케이스 구현 |
| Docker 환경 설정 | ✅ 완료 | Cluster, HA 설정 파일 존재 |
| 벤치마크 실행 | ⚠️ 부분 실패 | 환경 설정 문제로 중단 |
| 문서화 | ✅ 완료 | 사용 가이드, 튜닝 가이드 존재 |

---

## 📁 주요 파일 위치

```
valkey-vector-benchmark/
├── VectorDBBench/
│   ├── vectordb_bench/backend/clients/valkey/
│   │   ├── config.py              # 설정 클래스
│   │   ├── new_client.py           # 메인 클라이언트 구현
│   │   ├── cli.py                  # CLI 명령어
│   │   └── README.md               # 클라이언트 문서
│   ├── tests/test_valkey_client.py # 단위 테스트
│   ├── valkey_bench_config.yaml    # 벤치마크 설정 파일
│   ├── docker-compose.benchmark-cluster.yml
│   └── docker-compose.benchmark-ha.yml
└── docs/
    ├── manual_benchmark_guide.md
    ├── valkey_bench_result_summary.md
    └── valkey_hnsw_tuning.md
```

---

## 💡 참고 사항

- 벤치마크가 중단된 주요 원인은 **환경 설정 문제**입니다 (서버 미실행, 설정 불일치)
- 코드 구현 자체는 완료되어 있으며, 환경을 올바르게 설정하면 정상 동작할 것으로 예상됩니다
- 현재 `valkey_bench_config.yaml`에서 Cluster 케이스만 활성화되어 있으며, 노드 설정이 불완전합니다


