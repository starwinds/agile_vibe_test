import json
import logging
import httpx
import numpy as np
from typing import List, Dict, Any
from .schemas import SearchRequest, SearchResult
from .settings import settings
from .clients import RedisClient
from usecase_rag_highperf.app.common import pack_f32, EMBEDDING_DIM

logger = logging.getLogger(__name__)

async def embed_text_ollama(text: str) -> bytes:
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
    r = RedisClient.get_instance()
    
    # 1. Embed
    vec_bytes = await embed_text_ollama(req.query)
    
    # 2. Search
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
        logger.error(f"Semantic search failed: {e}")
        return []

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
        # Cosine distance is 0 (same) to 2 (opposite).
        # Similarity = 1 - distance/2 ? Or just 1 - distance (if normalized vectors and dist=1-cos)
        # Assuming RediSearch uses 1 - cosine_sim for distance.
        # So sim = 1 - dist.
        sim = 1.0 - dist 
        
        out.append(SearchResult(
            rank=item["rank"],
            doc_id=item["fields"].get("doc_id", "unknown"),
            snippet=item["fields"].get("chunk_text", "")[:200] + "...",
            content=item["fields"].get("chunk_text", ""),
            scores={"vector": sim, "distance": dist}
        ))
    return out

async def search_keyword(req: SearchRequest) -> List[SearchResult]:
    r = RedisClient.get_instance()
    
    # FT.SEARCH idx "query" WITHSCORES RETURN 2 doc_id chunk_text
    # Simple query parsing?
    # Escape special chars if needed.
    
    try:
        res = await r.execute_command(
            "FT.SEARCH", settings.VALKEY_INDEX, req.query,
            "WITHSCORES",
            "LIMIT", "0", str(req.top_k),
            "RETURN", "2", "doc_id", "chunk_text"
        )
    except Exception as e:
        logger.error(f"Keyword search failed: {e}")
        return []
        
    parsed = parse_redis_response(res, with_scores=True)
    
    # Explicitly fetch chunk_text for all results
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
        out.append(SearchResult(
            rank=item["rank"],
            doc_id=item["fields"].get("doc_id", "unknown"),
            snippet=item["fields"].get("chunk_text", "")[:200] + "...",
            content=item["fields"].get("chunk_text", ""),
            scores={"bm25": item["score"]}
        ))
    return out
