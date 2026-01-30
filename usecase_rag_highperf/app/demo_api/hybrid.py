from typing import List, Dict, Set
import asyncio
import logging
from .schemas import SearchRequest, SearchResult
from .search_valkey import search_semantic, search_keyword

logger = logging.getLogger(__name__)

def normalize_scores(results: List[SearchResult], score_key: str) -> Dict[str, float]:
    """
    Returns a dict {doc_id: normalized_score} where normalized_score is in [0, 1].
    """
    if not results:
        return {}
    
    scores = [r.scores.get(score_key, 0.0) for r in results]
    min_s = min(scores)
    max_s = max(scores)
    
    normalized = {}
    for r in results:
        val = r.scores.get(score_key, 0.0)
        if max_s - min_s == 0:
            # If all scores are the same, they all get 1.0 if > 0, else 0.0
            normalized[r.doc_id] = 1.0 if max_s > 0 else 0.0
        else:
            normalized[r.doc_id] = (val - min_s) / (max_s - min_s)
            
    return normalized

async def search_hybrid(req: SearchRequest) -> List[SearchResult]:
    # 1. Parallel search
    sub_k = req.top_k * 2
    
    sem_req = SearchRequest(query=req.query, top_k=sub_k, mode="semantic", engine=req.engine)
    key_req = SearchRequest(query=req.query, top_k=sub_k, mode="keyword")
    
    sem_res, key_res = await asyncio.gather(
        search_semantic(sem_req),
        search_keyword(key_req)
    )
    
    logger.info(f"Hybrid Search: Query='{req.query}' | Semantic={len(sem_res)} docs | Keyword={len(key_res)} docs")
    
    # 2. Normalize for weighted sum calculation
    # Note: We use "vector" for semantic and "bm25" for keyword.
    sem_norm_map = normalize_scores(sem_res, "vector")
    key_norm_map = normalize_scores(key_res, "bm25")
    
    # 3. Union Docs
    all_doc_ids = set(sem_norm_map.keys()) | set(key_norm_map.keys())
    
    # 4. Weighted Sum
    w_sem = req.weights.get("semantic", 0.5)
    w_key = req.weights.get("keyword", 0.5)
    
    # Helper to quickly find raw results
    raw_sem_map = {r.doc_id: r for r in sem_res}
    raw_key_map = {r.doc_id: r for r in key_res}
    
    merged_results = []
    
    for doc_id in all_doc_ids:
        # Normalized scores for calculation
        s_norm = sem_norm_map.get(doc_id, 0.0)
        k_norm = key_norm_map.get(doc_id, 0.0)
        
        final_score = (w_sem * s_norm) + (w_key * k_norm)
        
        # Determine which result object to use as base (prefer semantic)
        base_result = raw_sem_map.get(doc_id) or raw_key_map.get(doc_id)
        
        # Gather raw scores for display/debug
        raw_vector_score = raw_sem_map[doc_id].scores.get("vector", 0.0) if doc_id in raw_sem_map else 0.0
        raw_bm25_score = raw_key_map[doc_id].scores.get("bm25", 0.0) if doc_id in raw_key_map else 0.0
        
        merged_results.append(SearchResult(
            rank=0, # to be assigned
            doc_id=doc_id,
            snippet=base_result.snippet,
            content=base_result.content,
            scores={
                "vector": raw_vector_score, # RAW SCORE
                "bm25": raw_bm25_score,     # RAW SCORE
                "norm_vector": s_norm,      # Normalized for debug
                "norm_bm25": k_norm,        # Normalized for debug
                "final": final_score
            },
            source=f"hybrid({base_result.source})"
        ))
        
    # 5. Sort & Slice
    merged_results.sort(key=lambda x: x.scores["final"], reverse=True)
    
    final_out = merged_results[:req.top_k]
    
    # Assign Rank
    for i, r in enumerate(final_out):
        r.rank = i + 1
        
    return final_out