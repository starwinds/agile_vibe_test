import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from vectordb_bench.backend.clients.valkey.config import ValkeyDBConfig, ValkeyDBCaseConfig
from vectordb_bench.backend.clients.valkey.new_client import ValkeyClient
from vectordb_bench.backend.clients import MetricType

@pytest.fixture
def db_config():
    return ValkeyDBConfig(host="localhost", port=6379)

@pytest.fixture
def case_config():
    return ValkeyDBCaseConfig(
        index_name="test_idx",
        prefix="test_doc:",
        M=16,
        EF_CONSTRUCTION=200,
        EF_RUNTIME=10,
        distance_metric=MetricType.COSINE
    )

@pytest.fixture
def mock_valkey():
    with patch("vectordb_bench.backend.clients.valkey.new_client.valkey.Valkey") as mock:
        yield mock

def test_init_and_create_index(db_config, case_config, mock_valkey):
    client_instance = mock_valkey.return_value
    # Simulate index not existing
    client_instance.ft.return_value.info.side_effect = Exception("Index not found")
    
    client = ValkeyClient(dim=128, db_config=db_config, db_case_config=case_config, drop_old=True)
    
    # Verify connection
    mock_valkey.assert_called_with(
        host="localhost",
        port=6379,
        password=None,
        decode_responses=True
    )
    
    # Verify index creation
    client_instance.ft.assert_called_with("test_idx")
    client_instance.ft.return_value.create_index.assert_called_once()

def test_insert_embeddings(db_config, case_config, mock_valkey):
    client = ValkeyClient(dim=4, db_config=db_config, db_case_config=case_config)
    
    # When init() is called, it creates a new client instance.
    # We need to configure the mock to return a usable instance.
    # Since mock_valkey is the class, calling it returns a new instance.
    # We can use the same instance for simplicity or just let it create a new one.
    
    with client.init():
        # client.client is now set to a mock instance
        client_instance = client.client
        pipe = client_instance.pipeline.return_value
        
        embeddings = [
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8]
        ]
        metadata = [100, 200]
        
        client.insert_embeddings(embeddings, metadata)
        
        # Verify pipeline execution
        assert pipe.hset.call_count == 2
        pipe.execute.assert_called()

def test_search_embedding(db_config, case_config, mock_valkey):
    client = ValkeyClient(dim=4, db_config=db_config, db_case_config=case_config)
    
    with client.init():
        client_instance = client.client
        
        # Mock search response
        mock_doc = MagicMock()
        mock_doc.id = "test_doc:1"
        mock_doc.payload = {"id": "1", "score": "0.99"}
        
        mock_res = MagicMock()
        mock_res.docs = [mock_doc]
        client_instance.ft.return_value.search.return_value = mock_res
        
        query = [0.1, 0.2, 0.3, 0.4]
        results = client.search_embedding(query, k=1)
        
        assert len(results) == 1
        assert results[0] == 1
        client_instance.ft.return_value.search.assert_called_once()

def test_cleanup(db_config, case_config, mock_valkey):
    client = ValkeyClient(dim=4, db_config=db_config, db_case_config=case_config)
    
    # cleanup needs a connection. In __init__, it uses the temporary one.
    # If called externally, we might need to ensure connection exists.
    # My implementation of cleanup uses self.client.
    # So we should use init() here too.
    
    with client.init():
        client_instance = client.client
        client.cleanup()
        client_instance.ft.return_value.dropindex.assert_called_once_with(delete_documents=True)
