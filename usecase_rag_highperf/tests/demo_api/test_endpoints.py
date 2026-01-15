import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from usecase_rag_highperf.app.demo_api.schemas import SearchResult

@patch("usecase_rag_highperf.app.demo_api.main.search_semantic")
@patch("usecase_rag_highperf.app.demo_api.main.requests.get")
def test_search_endpoint_semantic(mock_get, mock_search):
    mock_get.return_value.status_code = 200 # Ollama OK
    
    mock_search.return_value = [
        SearchResult(rank=1, doc_id="d1", snippet="s1", scores={"vector": 0.9})
    ]
    
    from usecase_rag_highperf.app.demo_api.main import app
    with TestClient(app) as client:
        resp = client.post("/search", json={"query": "test", "mode": "semantic"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["doc_id"] == "d1"

@patch("usecase_rag_highperf.app.demo_api.main.search_hybrid")
@patch("usecase_rag_highperf.app.demo_api.main.requests.get")
def test_search_endpoint_hybrid(mock_get, mock_search):
    mock_get.return_value.status_code = 200
    
    mock_search.return_value = [
        SearchResult(rank=1, doc_id="d1", snippet="s1", scores={"final": 0.9})
    ]
    
    from usecase_rag_highperf.app.demo_api.main import app
    with TestClient(app) as client:
        resp = client.post("/search", json={"query": "test", "mode": "hybrid", "weights": {"semantic": 0.8, "keyword": 0.2}})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["doc_id"] == "d1"
