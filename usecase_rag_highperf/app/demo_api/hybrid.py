from typing import List, Dict, Set
from .schemas import SearchRequest, SearchResult
from .search_valkey import search_semantic, search_keyword

def normalize_scores(results: List[SearchResult], score_key: str) -> Dict[str, float]:
    """
    Returns a dict {doc_id: normalized_score}
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
            normalized[r.doc_id] = 1.0 if max_s > 0 else 0.0
        else:
            normalized[r.doc_id] = (val - min_s) / (max_s - min_s)
            
    return normalized

async def search_hybrid(req: SearchRequest) -> List[SearchResult]:
    # 1. Parallel search (could be optimized with asyncio.gather)
    # But for simplicity, we call them await sequentially or gather.
    # Let's use simple await first or gather if imported.
    import asyncio
    
    # We need to increase top_k for sub-queries to ensure overlap?
    # Usually we fetch top_k * 2 or similar.
    # Let's keep top_k for now or assume user passes large enough top_k.
    # To get good hybrid results, we usually fetch more candidates.
    sub_k = req.top_k * 2
    
    sem_req = SearchRequest(query=req.query, top_k=sub_k, mode="semantic")
    key_req = SearchRequest(query=req.query, top_k=sub_k, mode="keyword")
    
    sem_res, key_res = await asyncio.gather(
        search_semantic(sem_req),
        search_keyword(key_req)
    )
    
    # 2. Normalize
    # Semantic scores are already Similarity (0..1)? 
    # In search_valkey.py we calculated sim = 1 - dist.
    # If dist is not bounded 0..1, sim might not be either.
    # But Min-Max scaling is safer.
    
    sem_norm = normalize_scores(sem_res, "vector")
    key_norm = normalize_scores(key_res, "bm25")
    
    # 3. Union Docs
    all_docs = set(sem_norm.keys()) | set(key_norm.keys())
    
    # 4. Weighted Sum
    w_sem = req.weights.get("semantic", 0.5)
    w_key = req.weights.get("keyword", 0.5)
    
    merged_results = []
    
    # We need snippet and other info.
    # We prioritize info from semantic search, then keyword.
    doc_map = {r.doc_id: r for r in sem_res}
    for r in key_res:
        if r.doc_id not in doc_map:
            doc_map[r.doc_id] = r
            
    for doc_id in all_docs:
        s_score = sem_norm.get(doc_id, 0.0)
        k_score = key_norm.get(doc_id, 0.0)
        
        final_score = (w_sem * s_score) + (w_key * k_score)
        
        base_result = doc_map[doc_id]
        
        merged_results.append(SearchResult(
            rank=0, # to be assigned
            doc_id=doc_id,
            snippet=base_result.snippet,
            content=base_result.content,
            scores={
                "vector": sem_norm.get(doc_id, 0.0), # Store normalized for debug
                "bm25": key_norm.get(doc_id, 0.0),
                "final": final_score
            }
        ))
        
    # 5. Sort & Slice
    merged_results.sort(key=lambda x: x.scores["final"], reverse=True)
    
    final_out = merged_results[:req.top_k]
    
    # Assign Rank
    for i, r in enumerate(final_out):
        r.rank = i + 1
        
    return final_out
