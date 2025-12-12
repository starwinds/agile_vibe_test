# Valkey Standalone with Vector Search 설정 가이드

## 완료된 작업

### 1. Docker 이미지 비교 및 선정
- **선정 이미지**: `valkey/valkey-bundle:latest`
- **선정 이유**:
  - Valkey 서버와 모든 모듈이 포함됨
  - Search 모듈(벡터 검색 포함)이 사전 로드됨
  - 별도 설정 없이 바로 벡터 검색 사용 가능
  - 프로덕션 및 벤치마크에 적합

### 2. Dockerfile 작성
- **파일**: `Dockerfile.valkey-standalone`
- **기반 이미지**: `valkey/valkey-bundle:latest`
- **특징**: 
  - 벡터 검색 모듈이 자동으로 로드됨
  - 추가 설정 불필요

### 3. Docker Compose 설정
- **파일**: `docker-compose.valkey-standalone.yml`
- **기능**:
  - 포트 6379 노출
  - 데이터 영속성 (볼륨 마운트)
  - Health check 포함
  - 자동 재시작 설정

### 4. 구동 및 검증
- ✅ 컨테이너 정상 실행
- ✅ Search 모듈 로드 확인
- ✅ 벡터 인덱스 생성 성공
- ✅ 연결 테스트 성공

## 사용 방법

### 컨테이너 시작
```bash
cd /home/ubuntu/dev-proj/agile_vibe_test/valkey-vector-benchmark
docker-compose -f docker-compose.valkey-standalone.yml up -d
```

### 상태 확인
```bash
# 컨테이너 상태
docker ps | grep valkey-standalone

# 로그 확인
docker logs valkey-standalone

# 모듈 확인
docker exec valkey-standalone valkey-cli MODULE LIST

# 연결 테스트
docker exec valkey-standalone valkey-cli PING
```

### 벡터 인덱스 생성 예시
```bash
docker exec valkey-standalone valkey-cli FT.CREATE test_idx \
  ON HASH PREFIX 1 doc: \
  SCHEMA vector VECTOR HNSW 6 TYPE FLOAT32 DIM 100 DISTANCE_METRIC COSINE
```

### 컨테이너 중지
```bash
docker-compose -f docker-compose.valkey-standalone.yml down
```

## 로드된 모듈

다음 모듈들이 자동으로 로드됩니다:
- **search**: 벡터 검색 기능 (HNSW 지원)
- **json**: JSON 데이터 타입 지원
- **bf**: Bloom Filter
- **ldap**: LDAP 통합

## 벤치마크 실행

Valkey standalone이 실행된 상태에서 벤치마크를 실행할 수 있습니다:

```bash
cd VectorDBBench
source .venv/bin/activate
vectordbbench valkey --host 127.0.0.1 --port 6379 \
  --m 16 --ef-construction 200 --ef-runtime 10 \
  --db-label valkey-standalone
```

## 참고 문서

- [Docker 이미지 비교](./docker_image_comparison.md)
- [수동 벤치마크 가이드](./manual_benchmark_guide.md)

