import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# We will implement the app later, but we reference it here
# For TDD, this import might fail initially if the file doesn't exist.
# But we need to define the test first.

@patch("usecase_rag_highperf.app.demo_api.main.requests.get")
def test_health_check_endpoint(mock_get):
    # Mock successful connection
    mock_get.return_value.status_code = 200

    # Deferred import to allow test definition before implementation exists
    try:
        from usecase_rag_highperf.app.demo_api.main import app
    except ImportError:
        pytest.fail("Could not import app from usecase_rag_highperf.app.demo_api.main")

    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "ollama": "connected"}

@patch("usecase_rag_highperf.app.demo_api.main.requests.get")
def test_ollama_health_check_on_startup(mock_get):
    # Mock Ollama response
    mock_get.return_value.status_code = 200
    
    try:
        from usecase_rag_highperf.app.demo_api.main import app, check_ollama_connection
    except ImportError:
        pytest.fail("Could not import app or check_ollama_connection")

    # Call the check function directly to verify logic
    assert check_ollama_connection() is True
    
    # Test failure case
    mock_get.side_effect = Exception("Connection refused")
    assert check_ollama_connection() is False
