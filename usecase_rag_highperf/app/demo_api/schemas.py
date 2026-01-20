from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    mode: Literal["semantic", "keyword", "hybrid"] = "semantic"
    # hybrid weights: semantic_weight, keyword_weight
    weights: Optional[Dict[str, float]] = Field(default_factory=lambda: {"semantic": 0.5, "keyword": 0.5})

class SearchResult(BaseModel):
    rank: int
    doc_id: str
    snippet: str
    content: Optional[str] = None
    scores: Dict[str, float] # e.g. {"vector": 0.8, "bm25": 0.5, "final": 0.65}
    # Optional: full metadata if needed

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_found: int = 0
