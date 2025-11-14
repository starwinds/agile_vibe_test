from src.embedding import get_embedding

def test_embedding_shape():
    vec = get_embedding("Hello world")
    assert len(vec) == 384
