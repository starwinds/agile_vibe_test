import json
import pytest
from src.app import app
from src.db_utils import connect

# Import the fixture from test_db
from tests.test_db import db_conn

@pytest.fixture
def client():
    """Flask test client fixture."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_add_item_endpoint(client, db_conn):
    """
    Tests the POST /item endpoint.
    It uses the db_conn fixture to ensure a clean database.
    """
    # 1. Send a POST request
    item_data = {
        "item_name": "Test Item",
        "category": "Test Category",
        "content": "This is the content for the test item."
    }
    response = client.post('/item', data=json.dumps(item_data), content_type='application/json')

    # 2. Verify the response
    assert response.status_code == 201
    assert response.get_json() == {"message": "Item added successfully"}

    # 3. Query the database to confirm insertion
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM docs WHERE item_name = %s", ("Test Item",))
        result = cur.fetchone()
        assert result is not None
        assert result['category'] == "Test Category"
        assert result['content'] == "This is the content for the test item."

def test_search_endpoint(client, db_conn):
    """Tests the GET /search endpoint with and without category filter."""
    # 1. Populate the database with test data
    items = [
        {"item_name": "AI Book", "category": "Books", "content": "A book about artificial intelligence."},
        {"item_name": "Python Book", "category": "Books", "content": "A book about the Python language."},
        {"item_name": "CPU", "category": "Hardware", "content": "A metal box for storing clothes."}
    ]
    for item in items:
        client.post('/item', data=json.dumps(item), content_type='application/json')

    # 2. Test search without category filter
    response = client.get('/search?query=AI')
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) > 0
    assert results[0]['item_name'] == "AI Book"

    # 3. Test search with category filter
    response = client.get('/search?query=microprocessor&category=Hardware')
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == 0

    # 4. Test search with category filter that yields no results
    response = client.get('/search?query=AI&category=Hardware')
    assert response.status_code == 200
    results = response.get_json()
    assert len(results) == 0
