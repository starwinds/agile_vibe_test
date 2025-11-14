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
 ┃ ┣ sprint2_plan.md
 ┃ ┣ progress.md
 ┃ ┗ retro.md
 ┣ requirements.txt
 ┣ pytest.ini
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

### src/app.py
```python
from flask import Flask, request, jsonify, render_template_string
from .embedding import get_embedding
from .db_utils import connect, search_similar, insert_doc, create_index
import numpy as np
import uuid

app = Flask(__name__)

@app.route('/')
def hello_world():
    html_content = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>QA Service</title>
    <style>
        body { font-family: sans-serif; margin: 2em; }
        h1, h2 { color: #333; }
        form { margin-bottom: 2em; }
        label { display: block; margin-bottom: 0.5em; }
        input[type="text"], textarea { width: 100%; padding: 0.5em; margin-bottom: 1em; }
        #answer { background-color: #f0f0f0; padding: 1em; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>QA Service</h1>

    <h2>Ask a Question</h2>
    <form action="/qa" method="get" id="qa-form">
        <label>Question:</label>
        <input type="text" name="question">
        <button type="submit">Ask</button>
    </form>
    <div id="answer"></div>

    <h2>Add a Document</h2>
    <form action="/add_document" method="post" id="add-doc-form">
        <label>Document Content:</label>
        <textarea name="document" rows="5"></textarea>
        <button type="submit">Add Document</button>
    </form>
    <div id="add-doc-status"></div>
    <script>
        document.getElementById('qa-form').addEventListener('submit', async function(event) {
            event.preventDefault();
            const question = document.querySelector('#qa-form input[name="question"]').value;
            const responseDiv = document.getElementById('answer');
            responseDiv.innerHTML = 'Loading...';

            try {
                const response = await fetch(`/qa?question=${encodeURIComponent(question)}`);
                const data = await response.json();
                if (response.ok) {
                    responseDiv.innerHTML = `<strong>Answer:</strong> ${data.answer}`;
                } else {
                    responseDiv.innerHTML = `<strong>Error:</strong> ${data.error || 'Unknown error'}`;
                }
            } catch (error) {
                responseDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        });

        document.getElementById('add-doc-form').addEventListener('submit', async function(event) {
            event.preventDefault();
            const documentContent = document.querySelector('#add-doc-form textarea[name="document"]').value;
            const statusDiv = document.getElementById('add-doc-status');
            statusDiv.innerHTML = 'Adding document...';

            try {
                const response = await fetch('/add_document', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ document: documentContent })
                });
                const data = await response.json();
                if (response.ok) {
                    statusDiv.innerHTML = `<strong>Success:</strong> ${data.message} (ID: ${data.doc_id})`;
                    document.querySelector('#add-doc-form textarea[name="document"]').value = ''; // Clear textarea
                } else {
                    statusDiv.innerHTML = `<strong>Error:</strong> ${data.error || 'Unknown error'}`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        });
    </script>
</body>
</html>
"""
    return render_template_string(html_content)

@app.route('/qa', methods=['GET'])
def qa():
    question = request.args.get('question')
    if not question:
        return jsonify({"error": "Question parameter is required"}), 400

    query_embedding = get_embedding(question)
    # The vector from get_embedding is bytes, but search_similar expects a list/numpy array of floats.
    # Let's convert it back.
    query_vector = np.frombuffer(query_embedding, dtype=np.float32)

    conn = connect()
    results = search_similar(conn, query_vector, limit=1)

    if not results:
        return jsonify({"answer": "No similar documents found."})

    return jsonify({"answer": results[0]['content']})

@app.route('/add_document', methods=['POST'])
def add_document():
    data = request.get_json()
    document_content = data.get('document')

    if not document_content:
        return jsonify({"error": "Document content is required"}), 400

    doc_id = str(uuid.uuid4())
    embedding = get_embedding(document_content)

    conn = connect()
    insert_doc(conn, doc_id, document_content, embedding)

    return jsonify({"message": "Document added successfully", "doc_id": doc_id}), 201


if __name__ == '__main__':
    conn = connect()
    create_index(conn)
    app.run(debug=True)
```

### src/db_utils.py
```python
import redis
import numpy as np
from redis.commands.search.field import TagField, VectorField
from redis.commands.search.query import Query

def connect():
    return redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)

def create_index(conn):
    try:
        conn.ft("doc_index").info()
    except redis.exceptions.ResponseError:
        # Index does not exist, create it
        conn.ft("doc_index").create_index([
            TagField("content"),
            VectorField(
                "embedding",
                "HNSW",
                {"TYPE": "FLOAT32", "DIM": 384, "DISTANCE_METRIC": "COSINE"}
            )
        ])

def insert_doc(conn, doc_id, content, embedding):
    conn.hset(f"doc:{doc_id}", mapping={
        "content": content,
        "embedding": embedding
    })

def search_similar(conn, query_vec, limit=3):
    vec_bytes = np.array(query_vec, dtype=np.float32).tobytes()
    search_query = Query(f"*=>[KNN {limit} @embedding $vec AS score]")
    result = conn.ft("doc_index").search(
        search_query,
        query_params={"vec": vec_bytes}
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
python3 -m src.app # Flask 애플리케이션 실행
# 애플리케이션 시작 시 Valkey 인덱스가 자동으로 생성됩니다.
pytest --cov=src -v
```

---

## 📄 사용자 가이드 업데이트

자세한 애플리케이션 사용 방법은 다음 문서를 참조하십시오:
- valkey_agile_test/valkey-vector-app/docs/user_guide.md

---

## 📦 Gemini CLI 실행
```bash
gemini prompt -f setup_valkey_vector_app.md
```
