import os
import psycopg
import redis
import numpy as np
from typing import List, Dict
from dotenv import load_dotenv
from common import embed_text, pack_f32

load_dotenv()

# Valkey Connection
r = redis.Redis(
    host=os.getenv("VALKEY_HOST", "localhost"),
    port=int(os.getenv("VALKEY_PORT", 6379)),
    password=os.getenv("VALKEY_PASSWORD", "valkey"),
    decode_responses=False
)

INDEX_NAME = "idx:chunks"

def get_db_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "rag_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )

def search(query_text: str, tenant_id: str, principal: str, top_k: int = 5):
    """
    1. Embed query.
    2. ANN Search in Valkey.
    3. Filter results by ACL in Postgres.
    """
    # 1. Embed
    query_vector = embed_text(query_text)
    query_bytes = pack_f32(query_vector)
    
    # 2. Valkey Search
    # Query: (*)=>[KNN 5 @vector $vec]
    # Filter by tenant_id first? Yes, Hybrid Query.
    # (@tenant_id:{...})=>[KNN 5 @vector $vec]
    
    # We fetch 2x top_k to account for ACL filtering
    k_search = top_k * 2
    base_query = f"(@tenant_id:{{{tenant_id}}})=>[KNN {k_search} @vector $vec AS score]" 
    
    try:
        res = r.execute_command(
            "FT.SEARCH", INDEX_NAME, base_query,
            "PARAMS", "2", "vec", query_bytes,
            "DIALECT", "2",
            "RETURN", "2", "doc_id", "score"
        )
    except redis.exceptions.ResponseError as e:
        print(f"Search Error: {e}")
        return []

    # Parse results
    # Structure: [count, key, [field, val, ...], key, ...]
    
    total_hits = res[0]
    results = []
    
    hits = []
    # DIALECT 2 returns simple list of keys and field-values
    for i in range(1, len(res), 2):
        key = res[i]
        if isinstance(key, bytes):
            key = key.decode()
        
        # fields is a list [f1, v1, f2, v2...]
        fields_raw = res[i+1]
        fields = {}
        if fields_raw:
            for j in range(0, len(fields_raw), 2):
                f_name = fields_raw[j]
                f_val = fields_raw[j+1]
                if isinstance(f_name, bytes):
                    f_name = f_name.decode()
                if isinstance(f_val, bytes):
                    try:
                        f_val = f_val.decode()
                    except:
                        pass
                fields[f_name] = f_val
            
        hits.append({
            "chunk_key": key,
            "doc_id": fields.get("doc_id"),
            "score": fields.get("score")
        })

    if not hits:
        print("No matches in Valkey.")
        return []

    # 3. ACL Check in Postgres
    # Collect doc_ids
    doc_ids = list(set(h["doc_id"] for h in hits if h["doc_id"]))
    
    if not doc_ids:
        return []

    conn = get_db_connection()
    allowed_docs = set()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT doc_id FROM doc_acl
                WHERE tenant_id = %s
                  AND principal = %s
                  AND doc_id = ANY(%s)
            """, (tenant_id, principal, doc_ids))
            rows = cur.fetchall()
            allowed_docs = set(row[0] for row in rows)
    finally:
        conn.close()
        
    # Filter and Fetch Content
    final_results = []
    
    allowed_hits = [h for h in hits if h["doc_id"] in allowed_docs]
    allowed_hits = sorted(allowed_hits, key=lambda x: float(x["score"]) if x["score"] else 0) # Sort by score (distance, usually smaller is better for Cosine? Wait, Cosine in RediSearch: 1 - cosine_similarity. So smaller is closer/better)
    # Actually RediSearch Cosine is 1-cos, so 0 is identical, 1 is orthogonal, 2 is opposite.
    
    allowed_hits = allowed_hits[:top_k] # Limit to requested top_k
    
    if not allowed_hits:
        print("All matches filtered by ACL.")
        return []
        
    chunk_keys = [h["chunk_key"] for h in allowed_hits]
    chunk_ids = [k.split(":", 1)[1] for k in chunk_keys]
    
    # Fetch text
    conn = get_db_connection()
    chunk_texts = {}
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT chunk_id, chunk_text FROM chunks
                WHERE chunk_id = ANY(%s)
            """, (chunk_ids,))
            for row in cur.fetchall():
                chunk_texts[row[0]] = row[1]
    finally:
        conn.close()
        
    for h in allowed_hits:
        c_id = h["chunk_key"].split(":", 1)[1]
        final_results.append({
            "doc_id": h["doc_id"],
            "score": h["score"],
            "text": chunk_texts.get(c_id, "")
        })
        
    return final_results

if __name__ == "__main__":
    # Test Query
    results = search("Valkey", "tenant_a", "user:1")
    print(f"Found {len(results)} results:")
    for r in results:
        print(f"[Score: {r['score']}] Doc: {r['doc_id']} - {r['text'][:50]}...")
