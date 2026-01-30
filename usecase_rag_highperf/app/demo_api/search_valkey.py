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
    if not response:
        return []
    total = response[0]
    results = []
    if isinstance(total, bytes):
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
        fields = {}
        if isinstance(fields_raw, list):
            for i in range(0, len(fields_raw), 2):
                k = fields_raw[i].decode("utf-8") if isinstance(fields_raw[i], bytes) else fields_raw[i]
                v = fields_raw[i+1].decode("utf-8") if isinstance(fields_raw[i+1], bytes) else fields_raw[i+1]
                fields[k] = v
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
        return await _search_valkey(req, vec_bytes)

async def _search_valkey(req: SearchRequest, vec_bytes: bytes) -> List[SearchResult]:
    r = RedisClient.get_instance()
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
    vec = np.frombuffer(vec_bytes, dtype=np.float32)
    vec_list = vec.tolist()
    conn = await PostgresClient.connect()
    async with conn:
        async with conn.cursor() as cur:
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
    logger.info(f"Executing Keyword search via Postgres FTS for query: {req.query}")
    conn = await PostgresClient.connect()
    async with conn:
        async with conn.cursor() as cur:
            # Note: ts_rank can return 0 if the query matches but rank is very low.
            # Using ts_rank_cd or adding a small epsilon might help, 
            # but for keyword search we should at least see a match.
            await cur.execute("""
                SELECT c.doc_id, c.chunk_text, 
                       ts_rank(to_tsvector('english', c.chunk_text), plainto_tsquery('english', %s)) as score
                FROM chunks c
                WHERE to_tsvector('english', c.chunk_text) @@ plainto_tsquery('english', %s)
                ORDER BY score DESC
                LIMIT %s
            """, (req.query, req.query, req.top_k))
            rows = await cur.fetchall()
    out = []
    for rank, row in enumerate(rows, 1):
        doc_id, chunk_text, score = row
        # Ensure score is at least a small positive value if matched
        safe_score = float(score) if score > 0 else 0.0001
        logger.info(f"Match found: doc_id={doc_id}, score={score}, safe_score={safe_score}")
        out.append(SearchResult(
            rank=rank,
            doc_id=doc_id,
            snippet=chunk_text[:200] + "...",
            content=chunk_text,
            scores={"bm25": safe_score}, 
            source="postgres"
        ))
    return out
