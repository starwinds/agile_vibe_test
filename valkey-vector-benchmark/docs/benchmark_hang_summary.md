# 벤치마크 테스트 종료되지 않는 원인 요약

## 핵심 원인

**데이터셋 다운로드 단계에서 멈춤**

1. **Performance1536D50K 케이스**는 약 **450MB**의 데이터를 S3에서 다운로드해야 함
2. 다운로드 진행 상황이 명확하게 표시되지 않아 "멈춘 것"처럼 보임
3. 네트워크 속도에 따라 **수 분~수십 분** 소요 가능

## 확인된 사실

- 로컬에 부분 다운로드된 파일 존재: `shuffle_train.parquet` (76MB / 449MB)
- 벤치마크는 실제로 진행 중이지만, 다운로드 완료까지 대기 중
- 타임아웃이 24시간으로 설정되어 있어 즉시 실패하지 않음

## 해결 방법

### 즉시 해결: 작은 데이터셋 사용

현재 `valkey_bench_config.yaml`에 설정된 **glove-100-angular 10K** 케이스는:
- ❌ GLOVE 데이터셋은 1M만 지원 (10K 불가)
- ✅ **SIFT 100K** 또는 다른 작은 데이터셋 사용 권장

### 권장 실행 방법

```bash
cd VectorDBBench
source .venv/bin/activate

# SIFT 100K (128 dim, 작은 데이터셋)
vectordbbench valkey --host 127.0.0.1 --port 6379 \
  --m 16 --ef-construction 200 --ef-runtime 10 \
  --db-label valkey-standalone-sift \
  --case-type Performance768D100K
```

또는 현재 설정 파일의 **glove-100-angular**를 사용하려면:
- 데이터셋 크기를 1M으로 변경하거나
- 다른 작은 데이터셋으로 변경 필요

## 진행 상황 모니터링

별도 터미널에서 확인:
```bash
# 다운로드 진행 상황
watch -n 1 'ls -lh /tmp/vectordb_bench/dataset/'

# 실행 중인 프로세스
ps -ef | grep vectordbbench
```

