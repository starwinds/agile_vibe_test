# 🧭 Gemini CLI Prompt: Valkey + Valkey VectorSearch Python App Setup

## 🎯 목적
이 프로젝트는 **Valkey(오픈소스 Redis 포크)** 의 **VectorSearch 기능**을 활용하여  
Python 애플리케이션에서 문장 임베딩 데이터를 저장하고,  
코사인 유사도 기반의 벡터 검색을 수행하는 샘플 앱을 구축하기 위한 Agile + TDD 환경을 자동 구성하는 것을 목표로 합니다.

---

## ⚙️ 1️⃣ Valkey (VectorSearch, Docker)

```bash
docker run -d \
  --name valkey-vector \
  -p 6379:6379 \
  valkey/valkey:latest \
  --loadmodule /usr/lib/valkey/modules/vectorsearch.so
```

---

## 🧰 2️⃣ Python 환경 및 requirements.txt

```
redis==5.0.1
sentence-transformers==3.0.1
numpy>=1.26.0
pytest==8.3.2
pytest-cov==5.0.0
flask>=3.0.0
```

---

## 🧩 3️⃣ 프로젝트 구조

```
📦 valkey-vector-app/
 ┣ 📂 src/
 ┃ ┣ app.py
 ┃ ┣ db_utils.py
 ┃ ┗ embedding.py
 ┣ 📂 tests/
 ┃ ┣ test_embedding.py
 ┃ ┗ test_db.py
 ┣ 📂 docs/
 ┃ ┣ prd.md
 ┃ ┣ backlog.md
 ┃ ┣ sprint_plan.md
 ┃ ┣ progress.md
 ┃ ┗ retro.md
 ┣ requirements.txt
 ┗ README.md
```

---

## 🧠 4️⃣ 코드 스켈레톤

### src/embedding.py
```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")  # 384차원 모델

def get_embedding(text: str) -> bytes:
    embedding = model.encode(text)
    return np.array(embedding, dtype=np.float32).tobytes()
```

### src/db_utils.py
```python
import redis
import numpy as np

def connect():
    return redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)

def create_index(conn):
    try:
        conn.ft("doc_index").create_index([
            redis.commands.search.field.TextField("content"),
            redis.commands.search.field.VectorField(
                "embedding",
                "HNSW",
                {"TYPE": "FLOAT32", "DIM": 384, "DISTANCE_METRIC": "COSINE"}
            )
        ])
    except redis.ResponseError as e:
        if "Index already exists" not in str(e):
            raise

def insert_doc(conn, doc_id, content, embedding):
    conn.hset(f"doc:{doc_id}", mapping={
        "content": content,
        "embedding": embedding
    })

def search_similar(conn, query_vec, limit=3):
    vec_bytes = np.array(query_vec, dtype=np.float32).tobytes()
    query = f"*=>[KNN {limit} @embedding $vec AS score]"
    result = conn.ft("doc_index").search(
        query,
        query_params={"vec": vec_bytes},
        sort_by="score",
        dialect=2
    )
    docs = []
    for d in result.docs:
        docs.append({"id": d.id, "content": d.content, "score": float(d.score)})
    return docs
```

---


## 🧪 5️⃣ TDDD 방식 개발 가이드

### 개발 가이드 문서
- 아래 경로의 가이드 문서 참조

/home/ubuntu/dev-proj/valkey_agile_test/docs/dev_guide.txt


## 🧪 샘플 테스트 코드

### tests/test_embedding.py
```python
from src.embedding import get_embedding
import numpy as np

def test_embedding_shape():
    vec = get_embedding("Hello")
    assert isinstance(vec, bytes)
    assert len(np.frombuffer(vec, dtype=np.float32)) == 384
```

### tests/test_db.py
```python
from src.db_utils import connect, create_index, insert_doc, search_similar
from src.embedding import get_embedding
import numpy as np

def test_db_insert_and_search():
    conn = connect()
    create_index(conn)

    emb = get_embedding("AI development")
    insert_doc(conn, "1", "AI development", emb)

    q = np.frombuffer(get_embedding("artificial intelligence"), dtype=np.float32)
    results = search_similar(conn, q, limit=1)
    assert len(results) >= 1
```

---

## 📄 Agile 문서 세트

### docs/prd.md
- 프로젝트 개요, 목표, 사용자 시나리오, 기능 정의
- “PostgreSQL + pgvector 확장을 활용하여 문장 임베딩 저장 및 검색 기능 구현” 명시

### docs/backlog.md
- Epic/Story/Task 기반 정의
- 주요 항목: DB 설치, Embedding 생성, 검색, 테스트 자동화

### docs/sprint_plan.md
- Sprint 1 기간, 목표, Capacity, Definition of Done 포함

### docs/progress.md
- 날짜 / 작업 / 테스트 결과 / 커버리지 정리

### docs/retro.md
- 잘된 점 / 개선점 / 다음 스프린트 액션 아이템

---

## 🚀 실행

```bash
docker ps
source .venv/bin/activate
pytest --cov=src -v
```

---

## 📦 Gemini CLI 실행
```bash
gemini prompt -f setup_valkey_vector_app.md
```
