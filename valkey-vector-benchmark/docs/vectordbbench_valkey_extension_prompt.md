# VectorDBBench + Valkey 전용 클라이언트 개발 지시서 (Gemini CLI용 Prompt)

## 📌 00. 개발 목적

아래 요구 사항을 기반으로 VectorDBBench 코드베이스에 “Valkey” 전용 backend client를 신규 추가하는 개발 작업을 수행해 주세요.
최종 목표는 Valkey VectorSearch 기능을 표준 벡터 DB 벤치마크 흐름에 완전하게 통합하는 것입니다.

## 📌 01. 참고 Repo 정보 (반드시 이 코드베이스 기준으로 구현)

- **Repository:** https://github.com/zilliztech/VectorDBBench
- **Default Branch:** `main`
- **Backend Client 코드 위치:**
  ```
  vectordb_bench/backend/clients/
  ```
- **기존 클라이언트 참고 예시**
  - Redis: `vectordb_bench/backend/clients/redis/`
  - MemoryDB: `vectordb_bench/backend/clients/memorydb/`

---

## 🎯 1. 작업 목적

현재 VectorDBBench는 Valkey VectorSearch를 공식 지원하지 않음.  
Valkey의 HNSW 기반 벡터 검색을 정확하게 벤치마크할 수 있도록 **Valkey 전용 Backend Client**를 추가하여 다음 기능을 완전 지원하도록 확장한다:

- FT.CREATE 기반 인덱스 생성  
- Pipeline 기반 데이터 로딩  
- KNN(HNSW) 검색  
- Hybrid 검색(Tag + Numeric + Vector)  
- Cleanup 기능  

---

## 📁 2. 신규 개발 디렉토리 구조 (Repo 기준)

```
vectordb_bench/
 └─ backend/
     └─ clients/
         ├─ valkey/
         │   ├─ __init__.py
         │   ├─ config.py
         │   └─ new_client.py
         └─ __init__.py  # Valkey 등록 필요
```

---

## 🧩 3. 세부 구현 요구 사항

### A. config.py

**ValkeyDBConfig**
- host  
- port  
- password(SecretStr)

**ValkeyDBCaseConfig**
- index_name  
- prefix  
- M  
- EF_CONSTRUCTION  
- EF_RUNTIME  
- distance_metric (“COSINE” | “L2”)

---

### B. new_client.py

VectorDBBench의 `VectorDB` 추상 클래스 준수.  
Valkey 공식 Python SDK(**valkey-py**) 사용.

**필수 메서드**

1. `__init__()`  
   - 클라이언트 초기화  
   - `_init_index()` 호출  

2. `_init_index()`  
   - FT.CREATE 실행  
   - HASH 기반 스키마  
   - VECTOR(HNSW) 필드 생성  

3. `load(data_iter)`  
   - Pipeline 기반 처리  
   - `{prefix}{id}` 키 구조 사용  

4. `search(queries, top_k)`  
   - KNN 검색  
   - PARAMS 기반 벡터 전달  
   - 결과를 VectorDBBench 형식으로 변환  

5. `filtered_search(queries, filters, top_k)`  
   - Tag / Numeric 필터 결합  
   - Hybrid Query 구성  

6. `cleanup()`  
   - 인덱스 삭제  
   - prefix 기반 key 삭제(optional)

**인덱스 생성 예시**

```
FT.CREATE vdbbench_idx ON HASH PREFIX 1 doc:
SCHEMA id TAG metadata NUMERIC
vector VECTOR HNSW 6 TYPE FLOAT32 DIM <dim>
DISTANCE_METRIC <COSINE|L2> M <M> EF_CONSTRUCTION <value>
```

---

### C. clients/__init__.py 수정

DB enum 및 매핑에 Valkey 항목 추가:

```python
DB.Valkey: ValkeyClient
```

---

## 🧪 4. 테스트 요구 사항

아래 파일 생성:

```
tests/test_valkey_client.py
```

**테스트 항목**

1. 인덱스 생성 확인  
2. 1k 문서 로딩 및 시간 측정  
3. top-k 검색 정확도 확인  
4. Hybrid 검색 기능 검증  
5. cleanup 후 인덱스 존재 여부 점검  

---

## 📦 5. 최종 산출물 (Gemini가 생성해야 함)

- `config.py`
- `new_client.py`
- 수정된 `clients/__init__.py` diff
- `tests/test_valkey_client.py`
- README 문서 (사용법 및 예제)
- `valkey_bench_config.yaml`
- HNSW 튜닝 가이드 문서

---

## 📘 6. 추가 요구 사항

- Redis 코드 복사 금지 → Valkey Search 기준으로 신규 설계  
- FT.CREATE/SEARCH 구문은 Valkey Search 문법을 따른다  
- 타입 힌트 필수  
- VectorDBBench 인터페이스 구조 이해 후 정합성 유지  

---

## 🚀 7. 최종 작업 요청

Gemini, 아래 전체 요구 사항을 수행해 주세요.

다음 작업들은 GitHub Repository: https://github.com/zilliztech/VectorDBBench
 (main 브랜치 기준) 을 대상으로 합니다.

① Valkey 전용 Backend Client 전체 구현

아래 파일들을 신규 생성하여 Valkey VectorSearch 기능을 완전히 지원하는 클라이언트를 구현합니다:

vectordb_bench/backend/clients/valkey/config.py

vectordb_bench/backend/clients/valkey/new_client.py

vectordb_bench/backend/clients/valkey/__init__.py

vectordb_bench/backend/clients/__init__.py 패치 (DB.Valkey 등록)

구현 내용:

FT.CREATE 기반 HNSW/FLAT 인덱스 생성

Pipeline 기반 대량 데이터 로딩

Vector KNN 검색

Hybrid 검색(Tag + Numeric + Vector)

Cleanup 기능

타입 힌트 포함 및 VectorDBBench 추상 클래스 규약 준수

② Valkey 클라이언트를 사용한 테스트 자동화 코드 생성

아래 테스트 파일을 새로 작성합니다:

tests/test_valkey_client.py


테스트 항목:

인덱스 생성 성공 여부 확인

1,000개 데이터 로딩 및 시간 측정

top-k KNN 검색 정확도 및 정렬 확인

Hybrid 검색 기능 검증

cleanup 후 인덱스 삭제 확인

③ 실행 가능한 벤치마크 설정 파일 및 문서 생성

다음 산출물을 생성합니다:

valkey_bench_config.yaml (VectorDBBench 실행용)

README 문서(Valkey 클라이언트 사용법 + 예제 코드 + 실행 명령 포함)

HNSW 튜닝 가이드 (valkey_hnsw_tuning.md)

구성 예시 및 모범 사례 문서

④ Valkey 전용 클라이언트를 이용한 실제 VectorDBBench 실행 및 결과 산출

다음 과정을 자동화하거나 예시 스크립트를 포함하여 문서화해 주세요:

1) 벤치마크 실행

아래 명령을 사용하여 Valkey 인스턴스를 대상으로 실제 벡터 검색 벤치마크를 수행합니다:

vectordbbench test --config-file valkey_bench_config.yaml


또는 Web UI 기반 실행 시:

init_bench


→ DB 선택 항목에서 “Valkey”를 선택하여 동일 테스트 수행.

2) 테스트 시나리오 최소 2종 포함

FLAT 인덱스 기반 테스트

HNSW 인덱스 기반 테스트

각 시나리오에 대해 다음 지표를 수집하고 비교합니다:

QPS

평균 지연시간(latency avg)

p95 / p99 지연시간

Recall

데이터 로딩 속도

3) 결과 요약 파일 생성

다음 파일을 생성해 주세요:

valkey_bench_result_summary.md


내용 포함:

FLAT vs HNSW 성능 비교

파라미터(M, EF_CONSTRUCTION, EF_RUNTIME) 변화에 따른 추세

최대 처리량(saturation QPS)

실 서비스(DBaaS) 관점에서의 해석 및 권장 인덱스 설정

⑤ 필요한 경우 설계 상의 개선 제안 포함

Valkey Search API와 VectorDBBench 구조 사이에서
개선하거나 표준화할 부분이 있다면
설계 변경 제안 사항을 요약하여 추가해 주세요.

✅ Gemini, 위 ①~⑤ 전체 작업을 수행하고 필요한 모든 코드·문서·테스트·실행 예시를 생성해 주세요.
