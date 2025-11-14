import pytest
from pgvector.psycopg import register_vector
from src.db_utils import connect, create_table, insert_item, search_similar, search_similar_euclidean
from src.embedding import get_embedding

@pytest.fixture(scope="function")
def db_conn():
    """
    Pytest fixture to set up and tear down a database connection and schema
    for each test function.
    """
    conn = None
    try:
        # Connect to the database
        conn = connect()
        with conn.cursor() as cur:
            # Clean up and set up the schema
            cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            create_table(conn)
        
        # Yield the connection to the test
        yield conn
        
    finally:
        # Close the connection
        if conn:
            conn.close()

def test_db_insert_and_search(db_conn):
    """Tests cosine similarity search."""
    content = "AI is transforming industries."
    vec = get_embedding(content)
    insert_item(db_conn, "AI Article", "Technology", content, vec)
    
    results = search_similar(db_conn, vec, limit=1)
    
    assert len(results) > 0
    assert results[0]['item_name'] == "AI Article"
    assert results[0]['category'] == "Technology"
    assert 'similarity' in results[0]

def test_db_search_euclidean(db_conn):
    """Tests Euclidean distance search."""
    content = "Software engineering best practices."
    vec = get_embedding(content)
    insert_item(db_conn, "Software Manual", "Engineering", content, vec)
    
    results = search_similar_euclidean(db_conn, vec, limit=1)
    
    assert len(results) > 0
    assert results[0]['item_name'] == "Software Manual"
    assert results[0]['category'] == "Engineering"
    assert 'distance' in results[0]