# 벤치마크 테스트 종료되지 않는 원인 분석

## 문제 현상
벤치마크 테스트 실행 시 종료되지 않고 무한 대기 상태로 보이는 현상

## 근본 원인

### 1. 데이터셋 다운로드 단계 (가장 큰 원인)
- **위치**: `task_runner.py`의 `_pre_run()` → `dataset.prepare()`
- **문제**: 
  - `Performance1536D50K` 케이스는 약 **450MB**의 데이터를 S3에서 다운로드해야 함
  - 다운로드 진행 상황이 명확하게 표시되지 않음
  - 네트워크 속도에 따라 수 분~수십 분 소요 가능
- **코드 위치**: `vectordb_bench/backend/data_source.py`의 `AwsS3Reader.read()`

### 2. 데이터 삽입 단계
- **위치**: `new_client.py`의 `insert_embeddings()`
- **문제**:
  - 50K 벡터를 1000개씩 배치로 삽입
  - 각 배치마다 pipeline 실행
  - 진행 상황 로그가 배치 단위로만 출력됨
- **예상 소요 시간**: 데이터 크기와 네트워크에 따라 수 분~수십 분

### 3. 타임아웃 설정
- **LOAD_TIMEOUT**: 24시간 (86400초)
- 실제로는 진행 중이지만 타임아웃이 너무 길어 멈춘 것처럼 보임

## 해결 방법

### 방법 1: 작은 데이터셋 사용 (권장)
현재 `valkey_bench_config.yaml`에 이미 설정된 `glove-100-angular` 10K 케이스 사용:
- 데이터 크기: 약 10MB (다운로드 빠름)
- 벡터 수: 10,000개 (삽입 빠름)
- 차원: 100 (처리 빠름)

### 방법 2: 로컬 데이터셋 확인 및 사용
```bash
# 다운로드된 데이터 확인
ls -lh /tmp/vectordb_bench/dataset/

# 이미 다운로드된 데이터가 있으면 재다운로드 스킵
```

### 방법 3: 데이터셋 다운로드 상태 모니터링
```bash
# 별도 터미널에서 다운로드 진행 상황 확인
watch -n 1 'ls -lh /tmp/vectordb_bench/dataset/openai/openai_small_50k/'
```

### 방법 4: 커스텀 작은 데이터셋 생성
synthetic 데이터를 사용하여 다운로드 없이 테스트

## 현재 상태 확인

### 다운로드된 파일 확인
```bash
ls -lh /tmp/vectordb_bench/dataset/openai/openai_small_50k/
```

현재 상태:
- `shuffle_train.parquet`: 76MB (부분 다운로드됨, 전체는 449MB 필요)
- 다른 파일들 (test.parquet, neighbors.parquet 등) 누락 가능

### 벤치마크 진행 상황 확인
```bash
# 실행 중인 프로세스 확인
ps -ef | grep vectordbbench

# 로그 파일 확인 (있는 경우)
tail -f /path/to/benchmark.log
```

## 권장 사항

1. **소규모 데이터셋으로 시작**: `glove-100-angular` 10K 케이스 사용
2. **진행 상황 모니터링**: 별도 터미널에서 다운로드/삽입 진행 상황 확인
3. **타임아웃 조정**: 필요시 더 짧은 타임아웃 설정
4. **로컬 데이터 활용**: 이미 다운로드된 데이터 재사용

## 다음 단계

소규모 데이터셋(`glove-100-angular` 10K)으로 벤치마크를 실행하여 빠르게 결과를 확인하는 것을 권장합니다.

