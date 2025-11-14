from src.db_utils import connect, create_index, insert_doc, search_similar
from src.embedding import get_embedding
import numpy as np

def test_db_insert_and_search():
    conn = connect()
    create_index(conn)

    emb = get_embedding("AI development")
    insert_doc(conn, "1", "AI development", emb)

    q = np.frombuffer(get_embedding("artificial intelligence"), dtype=np.float32)
    results = search_similar(conn, q, limit=1)
    assert len(results) >= 1
