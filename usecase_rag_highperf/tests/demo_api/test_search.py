import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from usecase_rag_highperf.app.demo_api.schemas import SearchRequest

# Mock settings before importing modules that use it
@pytest.fixture
def mock_settings():
    with patch("usecase_rag_highperf.app.demo_api.settings.settings") as m:
        m.VALKEY_INDEX = "idx:test"
        yield m

@pytest.fixture
def mock_redis():
    with patch("usecase_rag_highperf.app.demo_api.clients.RedisClient.get_instance") as m:
        mock_instance = AsyncMock()
        m.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_search_semantic(mock_redis, mock_settings):
    from usecase_rag_highperf.app.demo_api.search_valkey import search_semantic
    
    # Mock embedding
    with patch("usecase_rag_highperf.app.demo_api.search_valkey.embed_text_ollama") as mock_embed:
        mock_embed.return_value = b'fake_vector_bytes'
        
        # Mock FT.SEARCH response
        # [total, key1, [field1, val1, ...], key2, ...]
        # key1 usually "chunk:..."
        # fields: "doc_id", "1", "chunk_text", "hello world", "score", "0.1" (distance)
        mock_redis.execute_command.return_value = [
            1, 
            b"chunk:1", [b"doc_id", b"d1", b"chunk_text", b"hello world", b"score", b"0.1"]
        ]
        
        req = SearchRequest(query="test", top_k=1, mode="semantic")
        results = await search_semantic(req)
        
        assert len(results) == 1
        assert results[0].doc_id == "d1"
        assert results[0].snippet == "hello world"
        # 1 - 0.1 = 0.9 (assuming score is distance)
        # But wait, FT.SEARCH KNN result score is distance. We usually want similarity or just distance.
        # Let's say we map distance to score: 1 - distance/2 or just 1/(1+d). 
        # For simplicity in this demo, let's just return raw distance or 1-distance.
        # If distance is cosine distance (0..2), 1 - distance might be negative.
        # Standard cosine similarity is 1 - cosine_distance.
        assert "vector" in results[0].scores

@pytest.mark.asyncio
async def test_search_keyword(mock_redis, mock_settings):
    from usecase_rag_highperf.app.demo_api.search_valkey import search_keyword
    
    # Mock FT.SEARCH response (Standard Text Search)
    # [total, key1, [field1, val1, ...]]
    # score is not returned by default unless WITHSCORES is used.
    # If WITHSCORES: key, score, [fields...] ? No, standard FT.SEARCH syntax is messy.
    # If we use RETURN, we get fields. SCORER BM25?
    # FT.SEARCH ... WITHSCORES returns score after key.
    # Response: [total, key1, score1, [fields1], key2, score2, [fields2]]
    
    mock_redis.execute_command.return_value = [
        1,
        b"chunk:2", b"1.5", [b"doc_id", b"d2", b"chunk_text", b"keyword match"]
    ]
    
    req = SearchRequest(query="test", top_k=1, mode="keyword")
    results = await search_keyword(req)
    
    assert len(results) == 1
    assert results[0].doc_id == "d2"
    assert results[0].scores["bm25"] == 1.5
