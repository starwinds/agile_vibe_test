# Gemini CLI 실행 지시용 프롬프트: RAG High-Perf 샘플 레포(WSL2 Ubuntu 기준)

아래 요구사항을 **그대로** 수행해서, 로컬에 **샘플 리포지토리**를 생성하고 실행까지 검증해 주세요.  
타겟 아키텍처는 **RAG High-Perf (Postgres SoR + Valkey(VectorSearch) Serving)** 입니다.

> 중요 조건
> - **WSL2 환경의 Ubuntu 터미널에서 실행**을 전제로 합니다.
> - Makefile / scripts 폴더는 **사용하지 않습니다.**
> - 아래에 제시된 **리포지토리 구조와 파일 내용이 모두 포함**되어야 합니다.
> - docker-compose로 Postgres(+pgvector)와 Valkey(bundle)를 띄우고, python 샘플(app)로 ingest → index → query 흐름을 검증합니다.

---

## 1) 목표

1. `docker compose up -d`로 다음을 기동
   - **Postgres**: `pgvector/pgvector:pg17` (vector extension 포함)
   - **Valkey**: `valkey/valkey-bundle:latest` (VectorSearch/FT.* 명령 지원 가정)
2. Python 샘플로 아래 end-to-end 플로우 검증
   - ingest: 문서/청크/ACL + outbox 이벤트 생성 (Postgres SoR)
   - indexer: outbox 소비 → embedding 생성(샘플 stub) → Valkey에 색인
   - query: Valkey KNN 검색(TopK) → Postgres에서 ACL/본문 fetch → 컨텍스트 출력

---

## 2) 생성해야 하는 리포지토리 구조(정확히)

아래 구조로 생성합니다(추가 파일은 있어도 되지만, 최소 아래 파일은 전부 있어야 함).

```text
rag-highperf-pg-valkey/
  README.md
  .env.example
  docker-compose.yml

  postgres/
    00_extensions.sql
    01_schema.sql
    02_seed.sql

  app/
    requirements.txt
    common.py
    ingest.py
    indexer.py
    query.py
    healthcheck.py
```

---

## 3) 파일 내용(그대로 생성)

### 3.1 `docker-compose.yml`

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg17
    container_name: rag_pg
    environment:
      POSTGRES_USER: ${PG_USER:-rag}
      POSTGRES_PASSWORD: ${PG_PASSWORD:-ragpass}
      POSTGRES_DB: ${PG_DB:-ragdb}
    ports:
      - "${PG_PORT:-5432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./postgres/00_extensions.sql:/docker-entrypoint-initdb.d/00_extensions.sql:ro
      - ./postgres/01_schema.sql:/docker-entrypoint-initdb.d/01_schema.sql:ro
      - ./postgres/02_seed.sql:/docker-entrypoint-initdb.d/02_seed.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${PG_USER:-rag} -d ${PG_DB:-ragdb} -h 127.0.0.1"]
      interval: 5s
      timeout: 3s
      retries: 20

  valkey:
    image: valkey/valkey-bundle:latest
    container_name: rag_vk
    ports:
      - "${VK_PORT:-6379}:6379"
    volumes:
      - vkdata:/data
    healthcheck:
      test: ["CMD", "valkey-cli", "PING"]
      interval: 5s
      timeout: 3s
      retries: 20

volumes:
  pgdata:
  vkdata:
```

---

### 3.2 `.env.example`

```bash
# Postgres
PG_USER=rag
PG_PASSWORD=ragpass
PG_DB=ragdb
PG_PORT=5432
PG_DSN=postgresql://rag:ragpass@localhost:5432/ragdb

# Valkey
VK_HOST=localhost
VK_PORT=6379
VK_PASSWORD=
```

---

## 4) Postgres 초기화 SQL

### 4.1 `postgres/00_extensions.sql`

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4.2 `postgres/01_schema.sql`

```sql
create table if not exists documents (
  doc_id        text primary key,
  tenant_id     text not null,
  title         text,
  version       int not null default 1,
  status        text not null default 'active',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table if not exists chunks (
  chunk_id      text primary key,
  doc_id        text not null references documents(doc_id),
  tenant_id     text not null,
  chunk_text    text not null,
  chunk_hash    text not null,
  lang          text,
  updated_at    timestamptz not null default now()
);

create table if not exists doc_acl (
  tenant_id     text not null,
  doc_id        text not null references documents(doc_id),
  principal     text not null,
  permission    text not null,
  primary key (tenant_id, doc_id, principal)
);

create table if not exists outbox_events (
  id            bigserial primary key,
  event_type    text not null,
  tenant_id     text not null,
  chunk_id      text,
  doc_id        text,
  payload       jsonb not null default '{}'::jsonb,
  created_at    timestamptz not null default now(),
  processed_at  timestamptz
);

create index if not exists idx_outbox_unprocessed
  on outbox_events(id) where processed_at is null;
```

### 4.3 `postgres/02_seed.sql`

```sql
-- seed는 비워둬도 됩니다(ingest에서 문서/ACL을 넣습니다).
```

---

## 5) Python 샘플 코드

### 5.1 `app/requirements.txt`

```text
psycopg[binary]==3.2.1
redis==5.0.7
numpy==2.0.1
```

### 5.2 `app/common.py`

```python
import hashlib
import numpy as np

EMBED_DIM = 384  # 샘플 차원 (실 embedding 모델 dim에 맞추세요)

def embed_text_stub(text: str, dim: int = EMBED_DIM) -> np.ndarray:
    # 데모용: 반드시 실제 embedding으로 교체하세요.
    h = hashlib.sha256(text.encode("utf-8")).digest()
    rnd = np.frombuffer((h * (dim * 4 // len(h) + 1))[: dim * 4], dtype=np.uint32)
    v = (rnd % 1000).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-9)
    return v

def pack_f32(vec: np.ndarray) -> bytes:
    return np.asarray(vec, dtype=np.float32).tobytes(order="C")
```

### 5.3 `app/ingest.py`

```python
import os, uuid, hashlib
from typing import List
import psycopg
from common import EMBED_DIM

def chunk_text(text: str, max_chars: int = 800, overlap: int = 80) -> List[str]:
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i+max_chars])
        i += max_chars - overlap
    return out

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def ingest_document(tenant_id: str, doc_id: str, title: str, text: str, principals_read: List[str]):
    dsn = os.environ["PG_DSN"]
    chunks = chunk_text(text)

    chunk_rows = []
    for idx, c in enumerate(chunks):
        chunk_id = f"{doc_id}:{idx}:{uuid.uuid4().hex[:8]}"
        chunk_rows.append((chunk_id, doc_id, tenant_id, c, sha1(c), "ko"))

    with psycopg.connect(dsn) as conn:
        with conn.transaction():
            conn.execute(
                """
                insert into documents(doc_id, tenant_id, title)
                values (%s,%s,%s)
                on conflict (doc_id) do update set
                  title=excluded.title,
                  version=documents.version+1,
                  updated_at=now()
                """,
                (doc_id, tenant_id, title),
            )

            conn.executemany(
                """
                insert into chunks(chunk_id, doc_id, tenant_id, chunk_text, chunk_hash, lang)
                values (%s,%s,%s,%s,%s,%s)
                on conflict (chunk_id) do update set
                  chunk_text=excluded.chunk_text,
                  chunk_hash=excluded.chunk_hash,
                  updated_at=now()
                """,
                chunk_rows,
            )

            conn.execute("delete from doc_acl where tenant_id=%s and doc_id=%s", (tenant_id, doc_id))
            conn.executemany(
                "insert into doc_acl(tenant_id, doc_id, principal, permission) values (%s,%s,%s,'read')",
                [(tenant_id, doc_id, p) for p in principals_read],
            )

            conn.executemany(
                """
                insert into outbox_events(event_type, tenant_id, chunk_id, doc_id, payload)
                values ('CHUNK_UPSERT', %s, %s, %s, jsonb_build_object('embed_dim', %s))
                """,
                [(tenant_id, r[0], doc_id, EMBED_DIM) for r in chunk_rows],
            )

    print(f"[ingest] doc_id={doc_id} chunks={len(chunk_rows)}")

if __name__ == "__main__":
    ingest_document(
        tenant_id="t1",
        doc_id="doc-001",
        title="Refund Policy",
        text=("환불은 결제일로부터 7일 이내 가능합니다. "
              "단, 디지털 상품은 다운로드 후 환불이 제한됩니다. "
              "반품/교환 절차는 고객센터 문의를 통해 진행합니다. ") * 20,
        principals_read=["user:alice", "group:support"],
    )
```

### 5.4 `app/indexer.py`

```python
import os, time
import psycopg
import redis
from common import embed_text_stub, pack_f32, EMBED_DIM

INDEX_NAME = "idx:chunks"
KEY_PREFIX = "chunk:"  # chunk:{tenant}:{chunk_id}

def vk_client() -> redis.Redis:
    host = os.environ.get("VK_HOST", "localhost")
    port = int(os.environ.get("VK_PORT", "6379"))
    pwd = os.environ.get("VK_PASSWORD") or None
    return redis.Redis(host=host, port=port, password=pwd, decode_responses=False)

def ensure_index(r: redis.Redis):
    try:
        r.execute_command("FT.INFO", INDEX_NAME)
        return
    except redis.ResponseError:
        pass

    # RedisSearch 계열 문법 예시(배포된 모듈 스펙에 맞게 조정 가능)
    r.execute_command(
        "FT.CREATE", INDEX_NAME,
        "ON", "HASH",
        "PREFIX", "1", KEY_PREFIX,
        "SCHEMA",
        "tenant_id", "TAG",
        "doc_id", "TAG",
        "chunk_id", "TEXT",
        "lang", "TAG",
        "updated_at", "NUMERIC",
        "embedding", "VECTOR", "HNSW",
            "6",
            "TYPE", "FLOAT32",
            "DIM", str(EMBED_DIM),
            "DISTANCE_METRIC", "COSINE",
    )
    print(f"[indexer] created index {INDEX_NAME}")

def process_batch(pg, r: redis.Redis, batch_size: int = 200) -> int:
    rows = pg.execute(
        """
        select id, tenant_id, chunk_id, doc_id, event_type
        from outbox_events
        where processed_at is null
        order by id
        limit %s
        """,
        (batch_size,),
    ).fetchall()

    if not rows:
        return 0

    for (eid, tenant_id, chunk_id, doc_id, event_type) in rows:
        if event_type == "CHUNK_DELETE":
            r.delete(f"{KEY_PREFIX}{tenant_id}:{chunk_id}")
        else:
            row = pg.execute(
                "select chunk_text, lang, extract(epoch from updated_at) from chunks where tenant_id=%s and chunk_id=%s",
                (tenant_id, chunk_id),
            ).fetchone()

            if not row:
                r.delete(f"{KEY_PREFIX}{tenant_id}:{chunk_id}")
            else:
                chunk_text, lang, updated_epoch = row
                vec = embed_text_stub(chunk_text)  # TODO: 실제 embedding으로 교체
                r.hset(f"{KEY_PREFIX}{tenant_id}:{chunk_id}", mapping={
                    b"tenant_id": tenant_id.encode(),
                    b"doc_id": doc_id.encode(),
                    b"chunk_id": chunk_id.encode(),
                    b"lang": (lang or "und").encode(),
                    b"updated_at": str(int(updated_epoch)).encode(),
                    b"embedding": pack_f32(vec),
                })

        pg.execute("update outbox_events set processed_at=now() where id=%s", (eid,))

    pg.commit()
    return len(rows)

def main():
    r = vk_client()
    ensure_index(r)

    with psycopg.connect(os.environ["PG_DSN"]) as pg:
        pg.autocommit = False
        print("[indexer] running...")
        while True:
            n = process_batch(pg, r)
            if n == 0:
                time.sleep(0.5)

if __name__ == "__main__":
    main()
```

### 5.5 `app/query.py`

```python
import os
import psycopg
import redis
from common import embed_text_stub, pack_f32

INDEX_NAME = "idx:chunks"

def vk_client() -> redis.Redis:
    host = os.environ.get("VK_HOST", "localhost")
    port = int(os.environ.get("VK_PORT", "6379"))
    pwd = os.environ.get("VK_PASSWORD") or None
    return redis.Redis(host=host, port=port, password=pwd, decode_responses=False)

def valkey_search(r: redis.Redis, tenant_id: str, lang: str, query: str, k: int = 30):
    qvec = embed_text_stub(query)
    blob = pack_f32(qvec)

    q = f"(@tenant_id:{{{tenant_id}}} @lang:{{{lang}}})=>[KNN {k} @embedding $vec AS score]"
    res = r.execute_command(
        "FT.SEARCH", INDEX_NAME,
        q,
        "PARAMS", "2", "vec", blob,
        "SORTBY", "score",
        "RETURN", "2", "chunk_id", "doc_id",
        "DIALECT", "2",
    )

    hits = []
    if not res or len(res) < 2:
        return hits

    i = 1
    while i < len(res):
        fields = res[i+1]
        d = {fields[j]: fields[j+1] for j in range(0, len(fields), 2)}
        hits.append((d.get(b"doc_id", b"").decode(), d.get(b"chunk_id", b"").decode()))
        i += 2
    return hits

def fetch_context(pg, tenant_id: str, principal: str, hits, limit_chars: int = 3000):
    doc_ids = sorted({d for d, _ in hits if d})
    if not doc_ids:
        return ""

    allowed = pg.execute(
        """
        select doc_id
        from doc_acl
        where tenant_id=%s and principal=%s and permission='read'
          and doc_id = any(%s)
        """,
        (tenant_id, principal, doc_ids),
    ).fetchall()
    allowed_docs = {r[0] for r in allowed}
    if not allowed_docs:
        return ""

    parts, total = [], 0
    for doc_id, chunk_id in hits:
        if doc_id not in allowed_docs:
            continue
        row = pg.execute(
            "select chunk_text from chunks where tenant_id=%s and chunk_id=%s",
            (tenant_id, chunk_id),
        ).fetchone()
        if not row:
            continue
        t = row[0].strip()
        if total + len(t) > limit_chars:
            break
        parts.append(t)
        total += len(t) + 2
    return "

".join(parts)

def main():
    tenant_id = "t1"
    principal = "user:alice"
    lang = "ko"
    query = "환불이 안돼요. 디지털 상품은 어떻게 되나요?"

    r = vk_client()
    hits = valkey_search(r, tenant_id, lang, query, k=40)
    print("[query] hits:", hits[:5])

    with psycopg.connect(os.environ["PG_DSN"]) as pg:
        ctx = fetch_context(pg, tenant_id, principal, hits)
    print("
=== CONTEXT ===
", ctx[:1500])

if __name__ == "__main__":
    main()
```

### 5.6 `app/healthcheck.py`

```python
import os
import psycopg
import redis

INDEX_NAME = "idx:chunks"

def main():
    with psycopg.connect(os.environ["PG_DSN"]) as pg:
        pg.execute("select 1").fetchone()
    print("[health] postgres: ok")

    r = redis.Redis(
        host=os.environ.get("VK_HOST", "localhost"),
        port=int(os.environ.get("VK_PORT", "6379")),
        password=(os.environ.get("VK_PASSWORD") or None),
        decode_responses=False,
    )
    pong = r.ping()
    print("[health] valkey: ok" if pong else "[health] valkey: fail")

    try:
        r.execute_command("FT.INFO", INDEX_NAME)
        print("[health] index:", INDEX_NAME, "ok")
    except Exception as e:
        print("[health] index:", INDEX_NAME, "not ready:", e)

if __name__ == "__main__":
    main()
```

---

## 6) README.md 작성 요구(실행 방법 포함)

`README.md`에는 아래 절차를 **명령어 그대로** 포함해 주세요.

### 6.1 WSL2 Ubuntu 터미널 실행 절차

```bash
# (권장) WSL 리눅스 파일시스템에 레포 생성
cd ~/work
mkdir -p rag-highperf-pg-valkey
cd rag-highperf-pg-valkey

# .env 생성
cp .env.example .env

# 컨테이너 기동
docker compose up -d
docker compose ps

# Python venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt

# .env export
set -a
source .env
set +a

# healthcheck
python app/healthcheck.py

# ingest (SoR에 저장 + outbox 생성)
python app/ingest.py

# indexer (별도 터미널에서 계속 실행 권장)
python app/indexer.py

# 다른 터미널에서 query
source .venv/bin/activate
set -a; source .env; set +a
python app/query.py
```

초기화가 필요하면:

```bash
docker compose down -v
docker compose up -d
```

---

## 7) 검증(필수)

1) `docker compose ps`에서 postgres/valkey가 healthy 상태인지 확인  
2) `python app/healthcheck.py` 실행 시
   - postgres ok
   - valkey ok
   - 인덱스는 indexer 실행 전이라 not ready일 수 있음(괜찮음)
3) `python app/ingest.py` 실행 시 `[ingest] doc_id=... chunks=...` 출력
4) `python app/indexer.py` 실행 시
   - 최초 `created index idx:chunks`가 출력되는지 확인
   - 이후 outbox가 처리되어 Valkey에 chunk keys가 생성되는지 확인
5) `python app/query.py` 실행 시
   - `[query] hits:`가 비어있지 않고
   - `=== CONTEXT ===` 아래에 텍스트가 출력되는지 확인

---

## 8) 추가 메모(문제 발생 시)

- 만약 Valkey에서 `FT.CREATE` 또는 `FT.SEARCH`가 실패하면,
  - `docker exec -it rag_vk valkey-cli MODULE LIST`
  - `docker exec -it rag_vk valkey-cli COMMAND INFO FT.SEARCH`
  결과를 함께 출력/기록하고, 오류 메시지를 README의 Troubleshooting 섹션에 추가해 주세요.
- 이 샘플은 embedding을 `embed_text_stub()`로 대체합니다. 실제 적용 시 사내 embedding 서비스 호출로 교체합니다.

---

## 9) 산출물

- 위 구조/파일이 포함된 `rag-highperf-pg-valkey/` 디렉토리
- WSL2 Ubuntu에서 위 실행 절차로 end-to-end 동작 확인
- 실행 로그(핵심 부분) README에 첨부
