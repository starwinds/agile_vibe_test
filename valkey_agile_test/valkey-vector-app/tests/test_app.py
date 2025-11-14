import pytest
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.mark.skip(reason="Skipping UI test to be replaced by manual testing.")
def test_root_endpoint_serves_html(client):
    """Test the root endpoint serves an HTML page with QA and document forms."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.data
    assert b'<h1>QA Service</h1>' in data
    assert b'<form action="/qa"' in data
    assert b'<input type="text" name="question">' in data
    assert b'<form action="/add_document"' in data
    assert b'<textarea name="document">' in data

def test_qa_endpoint(client, monkeypatch):
    """Test the /qa endpoint."""
    # Mock the search_similar function to return a predefined result
    def mock_search_similar(conn, query_vec, limit=3):
        return [{'content': 'mocked answer', 'score': 0.9}]

    monkeypatch.setattr('src.app.search_similar', mock_search_similar)

    response = client.get('/qa?question=test')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'answer' in json_data
    assert json_data['answer'] == 'mocked answer'

def test_add_document_endpoint(client, monkeypatch):
    """Test the /add_document endpoint."""
    # Mock the insert_doc function
    def mock_insert_doc(conn, doc_id, content, embedding):
        pass  # We don't need it to do anything for this test

    monkeypatch.setattr('src.app.insert_doc', mock_insert_doc)

    response = client.post('/add_document', json={'document': 'new test document'})
    assert response.status_code == 201
    json_data = response.get_json()
    assert 'message' in json_data
    assert json_data['message'] == 'Document added successfully'
    assert 'doc_id' in json_data
