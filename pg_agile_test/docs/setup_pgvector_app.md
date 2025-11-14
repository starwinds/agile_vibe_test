# 🧭 Gemini CLI Prompt: PostgreSQL + pgvector Python App Setup

## 🎯 목적
이 프로젝트는 **PostgreSQL 16 + pgvector 확장 기능**을 활용하여  
Python 애플리케이션에서 문장 임베딩 데이터를 저장하고,  
코사인 유사도 기반으로 검색하는 샘플 앱을 구축하기 위한 Agile + TDD 환경을 자동 구성하는 것을 목표로 합니다.

---

## ⚙️ 1️⃣ PostgreSQL (pgvector, Docker)

PostgreSQL + pgvector 환경을 Docker로 구성합니다.

```bash
docker run -d   --name pgvector-db   -e POSTGRES_PASSWORD=postgres   -p 5432:5432   ankane/pgvector:latest
```

상태 확인 및 접속:
```bash
docker ps
docker exec -it pgvector-db psql -U postgres
```

테스트 쿼리:
```sql
CREATE DATABASE vector_demo;
\c vector_demo;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE docs (
  id SERIAL PRIMARY KEY,
  content TEXT,
  embedding VECTOR(768)
);
```

---

## 🧰 2️⃣ Python 환경 및 requirements.txt

다음 내용으로 `requirements.txt` 파일을 생성하세요:

```
psycopg[binary,pool]==3.2.1
sentence-transformers==3.0.1
numpy>=1.26.0
pytest==8.3.2
pytest-cov==5.0.0
flask>=3.0.0
```

환경 설정 명령어 (`README.md` 에도 포함):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🧩 3️⃣ 프로젝트 구조

```
📦 pgvector-python-app/
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

model = SentenceTransformer("all-MiniLM-L6-v2")  # 384차원 모델 (VECTOR(384) 권장)

def get_embedding(text: str) -> list[float]:
    """텍스트를 임베딩 벡터로 변환"""
    embedding = model.encode(text)
    return embedding.tolist()
```

### src/db_utils.py
```python
import psycopg
from psycopg.rows import dict_row

def connect():
    return psycopg.connect("dbname=vector_demo user=postgres password=postgres host=127.0.0.1", row_factory=dict_row)

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS docs (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding VECTOR(384)
            );
        """)
    conn.commit()

def insert_vector(conn, text, vec):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO docs (content, embedding)
            VALUES (%s, %s)
        """, (text, vec))
    conn.commit()

def search_similar(conn, query_vec, limit=3):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, content,
                   1 - (embedding <#> %s) AS similarity
            FROM docs
            ORDER BY embedding <#> %s ASC
            LIMIT %s
        """, (query_vec, query_vec, limit))
        return cur.fetchall()
```

> 참고:  
> - pgvector 연산자 `<#>` = cosine 거리  
> - `<->` = Euclidean 거리  
> - `<=>` = inner product  

---

## 🧪 5️⃣ TDDD 방식 개발 가이드

### 개발 가이드 문서
- 아래 경로의 가이드 문서 참조

/home/ubuntu/dev-proj/pg_agile_test/docs/dev_guide.txt

### 샘플 테스트 코드

### tests/test_embedding.py
```python
from src.embedding import get_embedding

def test_embedding_shape():
    vec = get_embedding("Hello world")
    assert len(vec) in [384, 768]
```

### tests/test_db.py
```python
from src.db_utils import connect, create_table, insert_vector, search_similar
from src.embedding import get_embedding

def test_db_insert_and_search():
    conn = connect()
    create_table(conn)
    vec = get_embedding("AI development")
    insert_vector(conn, "AI development", vec)
    results = search_similar(conn, vec, limit=1)
    assert len(results) > 0
```

---

## 📘 6️⃣ Agile 문서 세트

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

## 🚀 7️⃣ 실행 및 검증 명령

```bash
# PostgreSQL 컨테이너 실행 확인
docker ps

# 가상환경 활성화 및 설치
source .venv/bin/activate
pip install -r requirements.txt

# pytest 실행
pytest --cov=src -v
```

---

## 🤖 8️⃣ Gemini CLI 협업 Prompt 예시

1. `generate pytest for new pgvector cosine search function`
2. `update docs/progress.md with today's pytest coverage`
3. `summarize sprint progress into markdown`
4. `refine backlog for sprint 2`
5. `suggest optimization for db_utils.py`

---

## 📦 9️⃣ 최종 지시

이 문서의 전체 내용을 참조하여 Gemini CLI는 다음을 수행해야 합니다.
1. `ankane/pgvector` Docker 컨테이너 기반 DB 환경 구성  
2. Python TDD 개발 환경 및 requirements.txt 설정  
3. Agile 문서 세트 생성  
4. 샘플 코드 및 테스트 스켈레톤 작성  
5. Markdown 형식으로 출력

---

### 실행 예시
```bash
gemini prompt -f setup_pgvector_app.md
```
