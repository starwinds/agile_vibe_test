import os
import sys
import redis
import psycopg
import numpy as np
from dotenv import load_dotenv

# Add parent dir to path to import common
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from common import pack_f32

load_dotenv()

def rebuild():
    # Valkey Connection
    r = redis.Redis(
        host=os.getenv("VALKEY_HOST", "localhost"),
        port=int(os.getenv("VALKEY_PORT", 6379)),
        password=os.getenv("VALKEY_PASSWORD", "valkey"),
        decode_responses=False
    )
    
    # Postgres Connection
    pg_conn = psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "rag_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )

    print("Fetching data from Postgres SoR...")
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT ce.chunk_id, ce.doc_id, ce.embedding, c.chunk_text, d.tenant_id
            FROM chunk_embeddings ce
            JOIN chunks c ON ce.chunk_id = c.chunk_id
            JOIN documents d ON c.doc_id = d.doc_id
        """)
        rows = cur.fetchall()

    print(f"Found {len(rows)} embeddings. Rebuilding Valkey index...")
    
    pipe = r.pipeline(transaction=False)
    count = 0
    for row in rows:
        chunk_id, doc_id, embedding_val, chunk_text, tenant_id = row
        
        # Handle vector format (psycopg3 usually adapts vector to list or numpy)
        if isinstance(embedding_val, str):
             # Fallback if returned as string
            import ast
            vec_list = ast.literal_eval(embedding_val)
            vec = np.array(vec_list, dtype=np.float32)
        elif isinstance(embedding_val, list):
            vec = np.array(embedding_val, dtype=np.float32)
        elif isinstance(embedding_val, np.ndarray):
            vec = embedding_val.astype(np.float32)
        else:
             # Try direct list conversion
             vec = np.array(list(embedding_val), dtype=np.float32)

        vector_bytes = pack_f32(vec)

        key = f"chunk:{chunk_id}"
        pipe.hset(key, mapping={
            "doc_id": doc_id,
            "tenant_id": tenant_id,
            "chunk_text": chunk_text,
            "vector": vector_bytes
        })
        count += 1
        if count % 1000 == 0:
            pipe.execute()
            print(f"Processed {count}...")
    
    pipe.execute()
    print(f"Rebuild complete. {count} chunks indexed.")
    pg_conn.close()

if __name__ == "__main__":
    rebuild()
