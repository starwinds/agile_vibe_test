# 벤치마크 실행 상태

## 현재 실행 중인 테스트

- **케이스**: Performance1536D50K (OpenAI 50K, 1536 dim)
- **DB**: Valkey Standalone
- **설정**: M=16, EF_CONSTRUCTION=200, EF_RUNTIME=10
- **프로세스 ID**: 17131
- **로그 파일**: `/tmp/valkey_benchmark_small.log`

## 현재 단계: 데이터셋 다운로드

다운로드 중인 파일 (총 4개, 약 450MB):
1. `shuffle_train.parquet` (449MB) - 학습 데이터
2. `neighbors.parquet` - Ground truth
3. `test.parquet` - 테스트 쿼리
4. `scalar_labels.parquet` - 스칼라 레이블

## 진행 상황 확인 방법

### 1. 로그 확인
```bash
tail -f /tmp/valkey_benchmark_small.log
```

### 2. 다운로드 진행 상황
```bash
watch -n 2 'ls -lh /tmp/vectordb_bench/dataset/openai/openai_small_50k/'
```

### 3. 프로세스 상태
```bash
ps -ef | grep vectordbbench
```

## 예상 소요 시간

- **다운로드**: 네트워크 속도에 따라 5-30분
- **데이터 삽입**: 5-15분
- **검색 테스트**: 10-20분
- **전체**: 약 20-65분

## 다음 단계

다운로드 완료 후 자동으로 진행:
1. 데이터 삽입 (Load)
2. 직렬 검색 테스트 (Search Serial)
3. 동시 검색 테스트 (Search Concurrent)

## 주의사항

- 다운로드 중에는 프로세스를 중단하지 마세요
- 네트워크 연결이 안정적인지 확인하세요
- 디스크 공간이 충분한지 확인하세요 (최소 1GB 여유 공간 필요)

