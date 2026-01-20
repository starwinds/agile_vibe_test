# 📌 배경 설명: Pattern A와 Pattern B의 차이와 진화 맥락

본 프로젝트는 **High-Performance RAG / Vector Search 데모**를 목표로 하며,
구현 복잡도를 단계적으로 관리하기 위해 **Pattern A → Pattern B** 순으로 진화하는 구조를 채택한다.

이 두 패턴은 **대체 관계가 아니라, 성숙도 단계의 차이**이다.

---

## Pattern A — Valkey-Centric Vector Search (Baseline / Demo-Friendly)

### 개요
Pattern A는 **Vector Search의 동작 원리와 성능 특성**을 빠르게 체감하기 위한 **최소 구성(minimal viable architecture)** 이다.

- Embedding은 **Indexer에서 생성**
- Embedding은 **Valkey(VectorSearch)에만 저장**
- PostgreSQL은 **텍스트(Source of Truth)와 Outbox만 담당**
- Valkey는 **검색 + 서빙을 동시에 담당**

### 구조 개념도
```
PostgreSQL (documents, chunks)
        + outbox
              ↓
          Indexer
        (embed 생성)
              ↓
      Valkey VectorSearch
```

### Pattern A의 한계
- Embedding 장기 보관 불가
- Valkey 장애 시 embedding 복구 불가
- embedding 모델 버전 관리 불가
- 검색 품질 기준선(baseline) 비교 불가

---

## Pattern B — PostgreSQL(pgvector) as Embedding SoR + Valkey Serving

### 개요
Pattern B는 Pattern A를 **운영/신뢰성 관점에서 보완**한 구조이다.

> **Embedding도 데이터이며,
> 데이터의 진실 원천(Source of Record)은 PostgreSQL이 맡는다.**

### 구조 개념도
```
PostgreSQL (SoR)
 ├─ documents / chunks
 ├─ chunk_embeddings (pgvector)
 └─ outbox_events
        ↓
     Indexer
   ↙           ↘
PG embedding   Valkey serving index
 upsert          upsert
```

### 핵심 차이 요약

| 구분 | Pattern A | Pattern B |
|----|----|----|
| Embedding 저장 | Valkey only | PostgreSQL(pgvector) |
| Valkey 역할 | 저장 + 서빙 | 서빙 전용 |
| Rebuild 가능 | ❌ | ✅ |
| Production 적합성 | 낮음 | 높음 |

---



# Gemini CLI Incremental Prompt — Pattern B Only
## PostgreSQL(pgvector) Embedding SoR + Valkey Serving (Incremental Extension)

이 문서는 **이미 Pattern A로 구현 완료된 프로젝트**를 전제로 하며,  
**기존 코드는 최대한 유지**한 채 **Pattern B(Embedding SoR = PostgreSQL)** 만을 **점진적으로 추가**하기 위한 작업 지시서입니다.

> 목표: “새로 만들기”가 아니라 **기존 구조 위에 안전하게 덧붙이기**

---

## 전제 조건 (As-Is 확인)

이미 구현되어 있다고 가정합니다.

- [x] 단일 tenant 구조
- [x] PostgreSQL: documents / chunks / outbox_events
- [x] Indexer:
  - outbox polling
  - embedding 생성(stub 또는 nomic)
  - Valkey VectorSearch 인덱스 upsert/delete
- [x] Valkey:
  - VECTOR 인덱스(HNSW)
- [x] Demo App:
  - semantic / keyword / hybrid 검색
  - explainability(score breakdown)

**주의:** 기존 로직은 깨지지 않아야 하며, 기본 동작은 계속 `engine=valkey` 기준으로 유지합니다.

---

## Phase 1 — PostgreSQL에 Embedding SoR 추가 (필수)

### 1.1 pgvector Extension 활성화
Postgres에 아래를 추가합니다.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 1.2 Embedding 테이블 추가
새 테이블만 추가합니다(기존 테이블 변경 금지).

```sql
CREATE TABLE chunk_embeddings (
  chunk_id     TEXT PRIMARY KEY,
  doc_id       TEXT NOT NULL,
  embedding    VECTOR(768) NOT NULL,
  model_name   TEXT NOT NULL,
  model_version TEXT NOT NULL,
  text_hash    TEXT NOT NULL,
  embedded_at  TIMESTAMPTZ DEFAULT now()
);
```

> embedding 차원(768)은 현재 사용 중인 모델 기준으로 맞추세요.

---

## Phase 2 — Indexer 확장 (핵심 변경점)

### 2.1 Outbox Payload는 변경하지 않는다
- outbox_events 구조/내용은 **절대 변경하지 않는다**
- embedding 벡터를 outbox에 싣지 않는다

### 2.2 CHUNK_UPSERT 처리 로직에 PG 저장 추가
기존 로직:

```
outbox → embed → Valkey upsert
```

변경 후 로직:

```
outbox
 → chunk_text 조회(Postgres)
 → embed 생성
 → PG chunk_embeddings UPSERT   ⭐ 추가
 → Valkey upsert (기존 유지)
```

#### UPSERT 규칙
- `chunk_id` 기준
- `text_hash` 동일하면 embedding 재계산/업데이트 생략 가능(옵션)
- 모델 정보(model_name/version) 함께 저장

### 2.3 CHUNK_DELETE 처리 로직 확장
기존:
- Valkey 인덱스 삭제

추가:
- PG `chunk_embeddings` row 삭제 또는 비활성화

---

## Phase 3 — Valkey 인덱스 Rebuild 기능 추가 (필수)

### 3.1 신규 스크립트 추가
파일 예시:

```
app/tools/rebuild_valkey_from_pg.py
```

### 3.2 동작 요구사항
1. Postgres에서 `chunk_embeddings` + 필요한 메타(chunk_text/title) 조회
2. Valkey 인덱스 초기화(DROP/CREATE 또는 전체 삭제)
3. batch 단위로 Valkey에 재적재
4. 진행률 로그 출력

> 이 스크립트는 **운영 안전장치**이며, Demo에서도 사용 가능해야 합니다.

---

## Phase 4 — Retrieval Engine 확장 (Demo/App)

### 4.1 pgvector Retrieval 추가
FastAPI에 **새 로직만 추가**합니다.

- pgvector 기반 KNN 검색
- 입력: query embedding
- 출력: 기존 SearchResult 형식과 동일

### 4.2 Engine 선택 파라미터 추가
기존 endpoint 유지 + query param 방식 권장:

```
POST /search/semantic?engine=valkey|pgvector|fallback
```

#### 동작 규칙
- `valkey`: 기존 동작 그대로
- `pgvector`: Postgres(pgvector)만 사용
- `fallback`: valkey 실패/timeout 시 pgvector로 재시도

---

## Phase 5 — Demo UI 최소 확장 (체감용)

### 5.1 Engine Selector 추가
Streamlit UI에 드롭다운 추가:

- Valkey (Fast)
- PGVector (Baseline)
- Fallback

### 5.2 Debug 표시 확장
Debug ON 시 반드시 표시:

- 실제 사용된 engine
- vector score(distance/similarity)
- fallback 발생 시 사유

---

## Phase 6 — 검증 시나리오 (필수)

아래 시나리오가 모두 가능해야 합니다.

1. **Valkey 정상**
   - engine=valkey → 빠른 응답
2. **Valkey 중단**
   - engine=fallback → pgvector 결과 반환
3. **Valkey 데이터 삭제**
   - rebuild_valkey_from_pg 실행
   - 동일 query 결과 복구

---

## Definition of Done (Pattern B Incremental)

필수:
- [ ] Postgres에 embedding 저장됨(pgvector)
- [ ] Indexer가 PG + Valkey 이중 반영
- [ ] Valkey rebuild 스크립트 동작
- [ ] Demo App에서 engine 전환 가능
- [ ] 기존 valkey-only 흐름 유지됨

금지:
- [ ] 기존 bench / demo 로직 제거
- [ ] outbox schema 변경
- [ ] 기존 API breaking change

---

## 핵심 원칙 요약

- **Postgres = Embedding SoR**
- **Valkey = 초저지연 Serving Index**
- **Outbox = 변경 사실 전달**
- **Rebuild 가능 = 운영 신뢰성**

이 prompt는 **Pattern A → Pattern B** 로의 *안전한 진화*를 목표로 합니다.

---
