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
