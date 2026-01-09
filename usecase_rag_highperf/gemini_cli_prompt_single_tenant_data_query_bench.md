# Gemini CLI 추가 작업 지시 Prompt
## High-Performance RAG Demo (Single Tenant) 고도화

아래 요구사항을 **모두 포함**하여 기존 `rag-highperf-pg-valkey` 샘플 레포지토리를 **확장 구현**해 주세요.  
목표는 **High Performance RAG 데모**를 위해 **현실적인 샘플 데이터/쿼리 생성기 + 벤치마크 스크립트**를 추가하는 것입니다.

---

## 0. 전제 조건

- **Single tenant만 고려**
  - tenant_id는 고정값 `t1`
- 멀티테넌시 로직은 제거
- ACL은 단순화
  - 기본은 모든 principal 접근 가능
  - (선택) 일부 문서(5% 내외)에 대해서만 `user:alice` 전용 ACL 적용 가능
- 기존 구조 유지
  - Postgres (SoR + outbox)
  - Valkey (VectorSearch serving)
  - indexer(outbox consumer) 구조 유지

---

## 1. 추가해야 할 파일 구조

기존 `app/` 디렉터리에 아래 파일들을 **추가**한다.

```text
app/
  generate_dataset.py      # 샘플 문서/청크/업데이트/삭제/outbox 생성
  generate_queries.py      # 벤치용 질의 세트 생성 (golden answer 포함)
  bench.py                 # 성능 벤치 스크립트
  metrics.py               # latency(p50/p95/p99), QPS 계산 유틸
```

기존 파일은 삭제하지 말고 **확장만 수행**한다.

---

## 2. 샘플 데이터 생성기 (`generate_dataset.py`)

### 2.1 목적
- 검색이 “필요해 보이는” **규모 있는 corpus** 자동 생성
- 문서 변경(업데이트/삭제)을 포함하여 **outbox + indexer**의 필요성을 데모

### 2.2 CLI 인터페이스
```bash
python app/generate_dataset.py   --docs 1500   --avg-chunks 12   --update-rate 0.08   --delete-rate 0.02   --seed 42
```

### 2.3 생성 데이터 요구사항

#### (1) 문서 도메인 (3종 이상)
1. **정책/FAQ**
   - 환불, 교환, 배송, 결제, 멤버십, 디지털 상품 제한
2. **운영 런북**
   - 장애 증상, 원인, 확인 절차, 조치 방법, 검증
   - 커맨드, 설정값, 에러코드 포함
3. **기술 문서**
   - API, 제한 사항, 에러코드(E429 등), 설정값(max_connections 등)

#### (2) 문서 특성
- 문서마다 고유 키워드 포함
  - 예: `E###`, `timeout=###`, `rate_limit`, `retry-after`, `max_connections`
- 비슷한 의미지만 표현이 다른 문장 다수 포함 (semantic search 데모용)

#### (3) 업데이트 / 삭제 이벤트
- 업데이트:
  - 전체 문서 중 `update-rate` 비율
  - version 증가(v2, v3)
  - 문장 일부 변경
  - 기존 chunk는 obsolete 처리, 신규 chunk 생성
  - `CHUNK_UPSERT` outbox 이벤트 생성
- 삭제:
  - 전체 문서 중 `delete-rate` 비율
  - status=deleted
  - `CHUNK_DELETE` outbox 이벤트 생성

#### (4) 산출물
- Postgres tables:
  - documents
  - chunks
  - (선택) doc_acl
  - outbox_events
- `data/manifest.json`
  - seed, docs 수, chunks 수, update/delete 비율 기록

---

## 3. 질의 생성기 (`generate_queries.py`)

### 3.1 목적
- 단일 쿼리가 아닌 **수백~수천 개 질의 세트** 생성
- 질의 유형별로 섞어서 검색 품질과 성능을 평가

### 3.2 CLI 인터페이스
```bash
python app/generate_queries.py   --queries 800   --mix semantic=0.50 keyword=0.25 hybrid=0.20 freshness=0.05   --seed 42
```

### 3.3 질의 유형 요구사항

#### (1) Semantic (약 50%)
- 문서 내용을 paraphrase한 자연어 질문
- 예:
  - “디지털 콘텐츠 다운로드 후 환불 가능한가요?”

#### (2) Keyword (약 25%)
- 에러코드/설정값 직접 질의
- 예:
  - “E429 에러는 무슨 의미인가?”
  - “max_connections 기본값?”

#### (3) Hybrid (약 20%)
- 키워드 + 자연어 혼합
- 예:
  - “E429가 뜨는데 rate limit 정책이 어떻게 되나요?”

#### (4) Freshness (약 5%)
- 업데이트된 문서의 **변경된 내용**을 묻는 질문
- 기대 결과는 최신 버전 문서

### 3.4 출력 포맷
- `data/queries.jsonl`
- 각 레코드는 다음 필드를 반드시 포함:

```json
{
  "query_id": "q-000123",
  "tenant_id": "t1",
  "principal": "user:alice",
  "query_type": "hybrid",
  "query_text": "E429가 뜨는데 rate limit 정책이 어떻게 되나요?",
  "expected_doc_ids": ["doc-1042"]
}
```

---

## 4. 벤치 스크립트 (`bench.py`)

### 4.1 목적
- High performance RAG 데모를 위한 **정량 지표 측정**
- p99 latency 중심

### 4.2 실행 모드 (최소 2개)

#### Mode A: `valkey_knn`
- Valkey VectorSearch만 수행
- 순수 retrieval latency 측정

#### Mode B: `hybrid_fetch`
- Valkey Top-K 후보 검색
- Postgres에서 chunk_text fetch
- end-to-end latency 측정

(pgvector 비교/fallback은 **이번 단계에서는 포함하지 않음**)

### 4.3 CLI 인터페이스
```bash
python app/bench.py   --queries data/queries.jsonl   --mode hybrid_fetch   --k 40   --concurrency 32   --duration-sec 60   --timeout-ms 200   --report out/bench_hybrid_fetch.json
```

### 4.4 측정 지표
- latency(ms): p50 / p95 / p99
- throughput(QPS 또는 req/sec)
- error rate / timeout rate
- hit@k
  - expected_doc_ids 중 하나라도 Top-K에 포함되면 hit

### 4.5 부하 방식
- **Closed-loop 방식**
  - worker N개
  - 응답 완료 후 다음 요청 전송
- `time.perf_counter_ns()` 기반 latency 측정

---

## 5. metrics 유틸 (`metrics.py`)

- percentile 계산(p50/p95/p99)
- QPS 계산
- 결과를 dict 형태로 반환하여 bench 결과에 포함

---

## 6. README 보강 요구사항

README에 아래 시나리오를 **명령어 그대로** 추가:

1. 데이터 생성
```bash
python app/generate_dataset.py --docs 1500 --avg-chunks 12 --seed 42
```

2. indexer 실행
```bash
python app/indexer.py
```

3. 질의 생성
```bash
python app/generate_queries.py --queries 800 --seed 42
```

4. 벤치 실행
```bash
python app/bench.py --mode hybrid_fetch --concurrency 32 --duration-sec 60
```

5. 데모 포인트 설명
- 대규모 corpus에서도 Valkey KNN p99가 낮음을 강조
- 업데이트/삭제 후에도 검색 결과가 최신 상태로 수렴함을 설명

---

## 7. 구현 시 주의사항

- 외부 데이터/API 사용 금지
- seed 고정 시 **재현 가능**해야 함
- embedding은 기존 `embed_text_stub()` 그대로 사용
- 코드 가독성 중시 (데모/교육 목적)

---

## 8. 최종 산출물

- 확장된 `app/` 코드
- `data/manifest.json`, `data/queries.jsonl`
- `out/bench_*.json` 벤치 결과
- README에 데모 실행 시나리오 명시

---

### 요약
이번 작업의 목적은 **멀티테넌시/ACL 고도화 이전 단계에서**
> “High performance RAG에서 왜 Valkey VectorSearch가 필요한지”  
> “outbox + indexer 구조가 왜 의미 있는지”  
를 **데이터 규모 + p99 지표**로 설득력 있게 보여주는 데 있다.
