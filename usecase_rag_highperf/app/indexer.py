import os
import json
import time
import redis
import psycopg
from dotenv import load_dotenv
from common import embed_text, pack_f32, EMBEDDING_DIM

load_dotenv()

# Valkey Connection
r = redis.Redis(
    host=os.getenv("VALKEY_HOST", "localhost"),
    port=int(os.getenv("VALKEY_PORT", 6379)),
    password=os.getenv("VALKEY_PASSWORD", "valkey"),
    decode_responses=False # We handle bytes for vectors
)

INDEX_NAME = "idx:chunks"

def find_dim(info):
    """
    Recursively find the value associated with 'DIM' or 'dimensions' in the nested list/dict structure.
    """
    if isinstance(info, list):
        for i, item in enumerate(info):
            # Check for DIM or dimensions (bytes or str)
            if item in (b'DIM', 'DIM', b'dimensions', 'dimensions'):
                if i + 1 < len(info):
                    try:
                        return int(info[i+1])
                    except (ValueError, TypeError):
                        pass
            res = find_dim(item)
            if res is not None:
                return res
    return None

def create_index():
    try:
        info = r.execute_command("FT.INFO", INDEX_NAME)
        existing_dim = find_dim(info)
        
        if existing_dim is not None and existing_dim != EMBEDDING_DIM:
            print(f"Index exists with DIM {existing_dim}, expected {EMBEDDING_DIM}. Dropping index...")
            r.execute_command("FT.DROPINDEX", INDEX_NAME)
            # Force raise to trigger creation block below
            raise redis.exceptions.ResponseError("Recreating")
        elif existing_dim is not None:
            print(f"Index exists with correct DIM {existing_dim}.")
            return
        else:
            print("Index exists but DIM not found. Assuming compatible.")
            return

    except redis.exceptions.ResponseError:
        print("Creating index...")
        # Schema: chunk_id (TAG), doc_id (TAG), tenant_id (TAG), vector (VECTOR)
        # Vector: HNSW, FLOAT32, DIM 384, DISTANCE COSINE
        # Note: FT.CREATE syntax might vary slightly depending on module version.
        # Below is standard RediSearch 2.x syntax.
        r.execute_command(
            "FT.CREATE", INDEX_NAME,
            "ON", "HASH",
            "PREFIX", "1", "chunk:",
            "SCHEMA",
            "doc_id", "TAG",
            "tenant_id", "TAG",
            "vector", "VECTOR", "HNSW", "6", "TYPE", "FLOAT32", "DIM", str(EMBEDDING_DIM), "DISTANCE_METRIC", "COSINE"
        )
        print("Index created.")

def process_events():
    pg_conn = psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "rag_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        autocommit=False
    )
    
    print("Starting Indexer Polling Loop...")
    
    try:
        while True:
            with pg_conn.cursor() as cur:
                # Fetch pending events
                cur.execute("""
                    SELECT event_id, event_type, payload
                    FROM outbox_events
                    WHERE status = 'PENDING'
                    ORDER BY created_at ASC
                    LIMIT 10
                    FOR UPDATE SKIP LOCKED
                """)
                events = cur.fetchall()
                
                if not events:
                    pg_conn.commit() # Release locks
                    time.sleep(1)
                    continue
                    
                for event_id, event_type, payload in events:
                    # payload is JSONB, so psycopg might return it as dict or str depending on config.
                    # With psycopg 3, it usually adapts JSONB to python objects automatically.
                    data = payload if isinstance(payload, dict) else json.loads(payload)
                    
                    if event_type == "CHUNK_UPSERT":
                        chunk_id = data["chunk_id"]
                        chunk_text = data["chunk_text"]
                        doc_id = data["doc_id"]
                        tenant_id = data["tenant_id"]
                        
                        # Generate Embedding
                        vector = embed_text(chunk_text)
                        vector_bytes = pack_f32(vector)
                        
                        # Index to Valkey
                        # Key: chunk:{chunk_id}
                        key = f"chunk:{chunk_id}"
                        r.hset(key, mapping={
                            "doc_id": doc_id,
                            "tenant_id": tenant_id,
                            "vector": vector_bytes
                        })
                        print(f"Indexed chunk {chunk_id}")
                        
                    elif event_type == "CHUNK_DELETE":
                        chunk_id = data["chunk_id"]
                        key = f"chunk:{chunk_id}"
                        r.delete(key)
                        print(f"Deleted chunk {chunk_id}")
                    
                    # Mark as processed
                    cur.execute("""
                        UPDATE outbox_events
                        SET status = 'PROCESSED', processed_at = CURRENT_TIMESTAMP
                        WHERE event_id = %s
                    """, (event_id,))
                
                pg_conn.commit()
                
    except KeyboardInterrupt:
        print("Stopping indexer...")
    except Exception as e:
        print(f"Error in indexer: {e}")
        pg_conn.rollback()
    finally:
        pg_conn.close()

if __name__ == "__main__":
    create_index()
    process_events()
