# Gemini CLI 구현 Prompt: Demo App (FastAPI API + Streamlit UI)
## High-Performance RAG Demo (Single Tenant) — Search Playground

아래 요구사항을 **모두 포함**하여, 기존 `gemini_cli_prompt_single_tenant_data_query_bench`로 완성된 레포지토리에 **End-user 체감형 Demo App**을 추가 구현하세요.  
벤치마크 코드는 **그대로 유지**하고, Demo App은 별도 경로로 추가합니다.

---

## 0) 목표 (What)
End-user 관점에서 아래를 **UI로 즉시 체감**할 수 있어야 합니다.

1. **Semantic Search(벡터)**: 표현이 달라도 의미 기반으로 잘 찾는다.
2. **Keyword Search(BM25)**: 에러코드/설정값 등 정확 키워드에 강하다.
3. **Hybrid Search(BM25 + Vector)**: 현업형 질문(키워드+의미 혼합)에 가장 강하다.
4. **Explainability(왜 이 결과인가?)**: 점수 breakdown/매칭 chunk/snippet으로 설명 가능하다.

> Non-goal: LLM 답변 생성(RAG generation)은 이번 범위에서 제외합니다.

---

## 1) 추가할 디렉터리/파일 구조

기존 구조를 유지하면서 아래를 추가합니다.

```text
app/
  demo_api/
    __init__.py
    main.py                # FastAPI 엔트리포인트
    settings.py            # 환경변수/설정 로드
    clients.py             # Valkey/Postgres 클라이언트 생성
    schemas.py             # Pydantic request/response 모델
    search_valkey.py       # semantic/keyword 쿼리 실행
    hybrid.py              # hybrid(2-pass union + rerank)
    utils_text.py          # snippet 생성/하이라이트
  streamlit_app/
    app.py                 # Streamlit UI (Search Playground)
    ui_presets.py          # 데모용 query preset
    api_client.py          # FastAPI 호출 래퍼
```

추가로 레포 루트에 실행/의존성을 위해 아래 파일을 추가하거나 수정합니다.

```text
requirements-demo.txt      # demo용 의존성(기존 requirements가 있으면 병합 가능)
README.md                  # Demo App 실행 방법/데모 시나리오 추가
```

---

## 2) FastAPI Demo API 설계

### 2.1 실행 방법(예시)
```bash
# 가상환경/의존성
pip install -r requirements-demo.txt

# API 실행
uvicorn app.demo_api.main:app --host 0.0.0.0 --port 8000
```

### 2.2 공통 Request/Response 포맷

#### Request (공통)
- `query`: string (사용자 입력)
- `top_k`: int (default 40)
- `debug`: bool (default false)
- `weights`: (hybrid에서만) `{ "keyword": 0.4, "vector": 0.6 }`
- `k_keyword`: (hybrid에서만) int (default 40)
- `k_vector`: (hybrid에서만) int (default 40)

#### Response (공통)
- `mode`: "semantic" | "keyword" | "hybrid"
- `query`: string
- `top_k`: int
- `results`: list[SearchResult]
- `meta`: latency_ms, counts, (debug이면) 후보 수 등

#### SearchResult 필드
- `rank`: int
- `doc_id`: string
- `title`: string
- `chunk_id`: string
- `snippet`: string (매칭 chunk_text 일부)
- `scores`:
  - semantic: `{ "vector": float }`
  - keyword: `{ "bm25": float }`
  - hybrid: `{ "bm25": float, "vector": float, "combined": float }`
- `debug`(optional):
  - `matched_terms`(keyword일 때)
  - `vector_distance_or_score`
  - `bm25_raw`
  - `normalization` 정보(선택)

### 2.3 엔드포인트
- `POST /search/semantic`
- `POST /search/keyword`
- `POST /search/hybrid`
- `GET  /health`
- `GET  /version` (optional: git sha, build time)

---

## 3) Valkey/Index 스키마 가정 및 쿼리 규칙

### 3.1 인덱스 스키마(기존 구현을 그대로 사용)
- `doc_id`, `title`, `chunk_id`, `chunk_text`(또는 text 필드), `embedding`(VECTOR), 기타 메타

### 3.2 Semantic Search (Vector)
- Valkey `FT.SEARCH`의 KNN 구문 사용
- 반환 필드에 `doc_id`, `title`, `chunk_id`, `chunk_text`(또는 snippet 생성용 텍스트), `score` 포함
- 점수 표기:
  - distance 기반이면 `vector`는 **낮을수록 좋음**이므로, UI 표기는 `similarity = 1/(1+distance)` 같은 간단 변환 또는 그대로 distance 표기(둘 중 하나로 통일)

### 3.3 Keyword Search (BM25)
- `FT.SEARCH idx "query"` 형태 사용
- `chunk_text` 텍스트 필드 기반 검색(BM25)
- `RETURN`에 동일 필드 포함
- 점수 표기:
  - `bm25`는 **높을수록 좋음**

### 3.4 Hybrid Search (2-pass union + rerank) — 데모용 표준
1) keyword top `k_keyword` 수행
2) vector top `k_vector` 수행
3) 후보 union(중복은 `chunk_id` 기준으로 제거)
4) 재정렬:
   - bm25 normalize: min-max 또는 rank-based normalize(간단히)
   - vector normalize: similarity로 변환 후 min-max 또는 rank-based normalize
   - `combined = w_keyword * bm25_norm + w_vector * vector_norm`
5) combined 기준 Top-K 반환
6) debug=true면 점수 breakdown 제공

> normalize는 너무 복잡하게 하지 말고, 데모 목적에 맞게 단순하고 재현 가능하게 구현합니다.

---

## 4) Postgres fetch(선택) 정책

Demo App에서는 **Valkey에서 반환된 chunk_text를 snippet으로 사용**해도 됩니다(초기 단순화).  
다만 기존 구조가 Postgres SoR를 가지고 있으므로, 옵션으로 아래를 지원합니다.

- `?fetch_source=pg` 옵션(또는 settings)로 켜면:
  - Valkey가 반환한 `chunk_id` 목록을 Postgres에서 일괄 조회해 `chunk_text`/`title`을 가져옵니다.
  - 이렇게 하면 “SoR fetch” 체감을 데모로 보여줄 수 있습니다.

초기 default는 `fetch_source=valkey`로 단순화하고, 설정으로 전환 가능하도록 하세요.

---

## 5) Streamlit UI 설계 (Search Playground)

### 5.1 실행 방법
```bash
streamlit run app/streamlit_app/app.py --server.port 8501
```

### 5.2 UI 요구사항(단일 화면)
좌측(또는 상단) 컨트롤:
- Query 입력창 (Enter로 실행)
- Mode 선택: Semantic / Keyword / Hybrid
- Top-K 선택: 20/40/80
- Debug 토글
- (Hybrid일 때만) 가중치 슬라이더:
  - keyword weight (0.0~1.0)
  - vector weight = 1 - keyword weight
- (선택) 결과 표시 개수(Top-N) / snippet 길이

우측(또는 하단) 결과 영역:
- 결과 리스트 카드/테이블
  - Rank, Title, Snippet, Score 요약
- Debug ON 시 확장 표시:
  - chunk_id
  - bm25/vector/combined breakdown
  - (선택) 하이라이트된 용어

### 5.3 Demo용 Query Preset 버튼(필수)
버튼 9개(권장)를 UI에 배치하고, 클릭 시 Query가 입력되고 실행되도록 합니다.

Semantic 3개:
- “다운로드한 디지털 콘텐츠도 결제 취소가 되나요?”
- “배송이 늦을 때 보상 규정이 있어요?”
- “결제 취소 절차가 어떻게 되나요?”

Keyword 3개:
- “E429”
- “max_connections”
- “retry-after”

Hybrid 3개:
- “E429가 뜨는데 rate limit 정책이 어떻게 되나요?”
- “timeout=110 뜰 때 조치 방법과 재시도 규칙?”
- “HTTP 429 재발 방지 설정 값 추천?”

> 데이터 생성기에서 위 키워드가 corpus에 충분히 존재하도록 이미 설계되어 있습니다.

---

## 6) requirements-demo.txt

필요 최소 패키지(버전은 최신 안정판 범위에서 지정):

- fastapi
- uvicorn[standard]
- pydantic
- streamlit
- httpx (streamlit→api 호출)
- redis (valkey 연결용)
- psycopg (또는 psycopg2-binary) (postgres fetch 옵션용)
- python-dotenv (선택: .env 로드)

기존 requirements가 있다면 중복 없이 병합해도 됩니다.

---

## 7) README.md 업데이트 요구사항

README에 아래 섹션을 추가:

### Demo App 실행
1) 데이터 생성 → indexer → 질의 생성(기존대로)
2) FastAPI 실행 명령
3) Streamlit 실행 명령
4) Demo 시나리오(10분 스크립트) 요약:
   - Semantic 강점 쿼리
   - Keyword 강점 쿼리
   - Hybrid 강점 쿼리
   - Debug로 왜 결과가 나왔는지 설명

---

## 8) 구현 품질/제약

- 외부 API 금지(데이터/LLM 호출 금지)
- 결과는 seed 고정 시 재현 가능해야 함
- 코드 가독성/설명 주석 적절히 추가
- 오류 메시지는 사용자가 이해 가능한 형태로 반환
- 성능 측정은 Demo App 범위에서 간단히(latency_ms)만 제공(벤치와 별개)

---

## 9) 최종 산출물 체크리스트

- [ ] FastAPI Demo API 3 엔드포인트 동작
- [ ] Streamlit UI에서 모드 변경 시 결과 차이가 체감됨
- [ ] Preset 버튼 9개 동작
- [ ] Debug ON 시 score breakdown/why 표시
- [ ] README에 실행 및 데모 시나리오 포함
- [ ] 벤치마크 구현 내역은 변경하지 않음

---

## 10) 참고: 기본 환경변수(.env 예시)

```bash
VALKEY_HOST=localhost
VALKEY_PORT=6379
VALKEY_PASSWORD=
VALKEY_INDEX=idx:chunks

POSTGRES_DSN=postgresql://postgres:postgres@localhost:5432/postgres

DEMO_FETCH_SOURCE=valkey  # valkey|pg
DEMO_API_BASE_URL=http://localhost:8000
```

---
