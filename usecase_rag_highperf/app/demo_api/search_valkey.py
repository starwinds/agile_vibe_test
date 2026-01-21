import json
import logging
import httpx
import numpy as np
from typing import List, Dict, Any
from .schemas import SearchRequest, SearchResult
from .settings import settings
from .clients import RedisClient, PostgresClient
from usecase_rag_highperf.app.common import pack_f32, EMBEDDING_DIM

logger = logging.getLogger(__name__)

async def embed_text_ollama(text: str) -> bytes:
    # Add prefix for nomic-embed-text
    if settings.OLLAMA_MODEL.startswith("nomic") and not text.startswith("search_query:"):
        text = f"search_query: {text}"

    url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": text
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
            embedding = data.get("embedding")
            if not embedding:
                raise ValueError("No embedding in response")
            
            vec = np.array(embedding, dtype=np.float32)
            # Normalize
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            
            return pack_f32(vec)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise e

def parse_redis_response(response: List[Any], with_scores: bool = False, vector_score_field: str = None) -> List[Dict[str, Any]]:
    """
    Parses raw FT.SEARCH response.
    Format with WITHSCORES: [total, key1, score1, [field1, val1, ...], key2, score2, ...]
    Format without WITHSCORES (but with params return): [total, key1, [field1, val1, ...], ...]
    Format with KNN vector score: [total, key1, [field1, val1, ..., vector_score_field, score], ...]
    """
    if not response:
        return []
        
    total = response[0]
    results = []
    
    # Check if response[0] is int (count)
    if isinstance(total, bytes):
        # Error or something unexpected
        return []

    idx = 1
    rank = 1
    while idx < len(response):
        key = response[idx]
        idx += 1
        
        score = 0.0
        if with_scores:
            score = float(response[idx])
            idx += 1
            
        fields_raw = response[idx]
        idx += 1
        
        # Parse fields (list of k, v)
        fields = {}
        if isinstance(fields_raw, list):
            for i in range(0, len(fields_raw), 2):
                k = fields_raw[i].decode("utf-8") if isinstance(fields_raw[i], bytes) else fields_raw[i]
                v = fields_raw[i+1].decode("utf-8") if isinstance(fields_raw[i+1], bytes) else fields_raw[i+1]
                fields[k] = v
        
        # If vector search, score might be in fields
        if vector_score_field and vector_score_field in fields:
            score = float(fields[vector_score_field])
            
        results.append({
            "key": key.decode("utf-8") if isinstance(key, bytes) else key,
            "score": score,
            "fields": fields,
            "rank": rank
        })
        rank += 1
        
    return results

async def search_semantic(req: SearchRequest) -> List[SearchResult]:
    # 1. Embed
    try:
        vec_bytes = await embed_text_ollama(req.query)
    except Exception as e:
        logger.error(f"Failed to embed query: {e}")
        return []

    if req.engine == "valkey":
        return await _search_valkey(req, vec_bytes)
    elif req.engine == "pgvector":
        return await _search_pgvector(req, vec_bytes)
    elif req.engine == "fallback":
        try:
            return await _search_valkey(req, vec_bytes)
        except Exception as e:
            logger.warning(f"Valkey search failed, falling back to PG: {e}")
            return await _search_pgvector(req, vec_bytes)
    else:
        # Default to valkey
        return await _search_valkey(req, vec_bytes)

async def _search_valkey(req: SearchRequest, vec_bytes: bytes) -> List[SearchResult]:
    r = RedisClient.get_instance()
    # FT.SEARCH idx "*=>[KNN k @vector $vec AS vector_score]" PARAMS 2 vec <bytes> DIALECT 2 RETURN 3 doc_id chunk_text vector_score
    query_str = f"*=>[KNN {req.top_k} @vector $vec AS vector_score]"
    
    try:
        res = await r.execute_command(
            "FT.SEARCH", settings.VALKEY_INDEX, query_str,
            "PARAMS", "2", "vec", vec_bytes,
            "DIALECT", "2",
            "RETURN", "3", "doc_id", "chunk_text", "vector_score"
        )
    except Exception as e:
        logger.error(f"Semantic search failed (Valkey): {e}")
        raise e

    parsed = parse_redis_response(res, with_scores=False, vector_score_field="vector_score")
    
    # Explicitly fetch chunk_text for all results to ensure we get content
    if parsed:
        keys = [item["key"] for item in parsed]
        async with r.pipeline() as pipe:
            for key in keys:
                pipe.hget(key, "chunk_text")
            chunks = await pipe.execute()
        
        for i, chunk in enumerate(chunks):
            if chunk:
                parsed[i]["fields"]["chunk_text"] = chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk

    out = []
    for item in parsed:
        dist = item["score"]
        # Convert distance to similarity score for display (0..1)
        sim = 1.0 - dist 
        
        out.append(SearchResult(
            rank=item["rank"],
            doc_id=item["fields"].get("doc_id", "unknown"),
            snippet=item["fields"].get("chunk_text", "")[:200] + "...",
            content=item["fields"].get("chunk_text", ""),
            scores={"vector": sim, "distance": dist},
            source="valkey"
        ))
    return out

async def _search_pgvector(req: SearchRequest, vec_bytes: bytes) -> List[SearchResult]:
    logger.info("Executing PGVector search with explicit vector cast.")
    vec = np.frombuffer(vec_bytes, dtype=np.float32)
    vec_list = vec.tolist()
    
    conn = await PostgresClient.connect()
    async with conn:
        async with conn.cursor() as cur:
            # chunk_embeddings join chunks
            # We convert vec_list to string "[0.1, 0.2, ...]" so psycopg passes it as text,
            # allowing explicit cast ::vector to work properly in Postgres.
            await cur.execute("""
                SELECT ce.doc_id, c.chunk_text, (ce.embedding <=> %s::vector) as distance
                FROM chunk_embeddings ce
                JOIN chunks c ON ce.chunk_id = c.chunk_id
                ORDER BY distance ASC
                LIMIT %s
            """, (str(vec_list), req.top_k))
            rows = await cur.fetchall()
            
    out = []
    for rank, row in enumerate(rows, 1):
        doc_id, chunk_text, distance = row
        # pgvector distance is typically 0..2 for cosine (1-cos) or 0..sqrt(2) for euclidean?
        # <=> is cosine distance operator. 0 is exact match, 1 is orthogonal, 2 is opposite.
        sim = 1.0 - distance
        out.append(SearchResult(
            rank=rank,
            doc_id=doc_id,
            snippet=chunk_text[:200] + "...",
            content=chunk_text,
            scores={"vector": sim, "distance": distance},
            source="pgvector"
        ))
    return out

async def search_keyword(req: SearchRequest) -> List[SearchResult]:
    logger.info(f"Executing Keyword search via Postgres ILIKE for query: {req.query}")
    
    conn = await PostgresClient.connect()
    async with conn:
        async with conn.cursor() as cur:
            # Simple ILIKE search on chunk_text
            search_pattern = f"%{req.query}%"
            await cur.execute("""
                SELECT c.doc_id, c.chunk_text
                FROM chunks c
                WHERE c.chunk_text ILIKE %s
                LIMIT %s
            """, (search_pattern, req.top_k))
            rows = await cur.fetchall()
            
    out = []
    for rank, row in enumerate(rows, 1):
        doc_id, chunk_text = row
        out.append(SearchResult(
            rank=rank,
            doc_id=doc_id,
            snippet=chunk_text[:200] + "...",
            content=chunk_text,
            scores={"bm25_simulated": 1.0}, # ILIKE doesn't give scores, using 1.0
            source="postgres"
        ))
    return out