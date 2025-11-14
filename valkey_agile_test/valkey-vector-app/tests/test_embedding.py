from src.embedding import get_embedding
import numpy as np

def test_embedding_shape():
    vec = get_embedding("Hello")
    assert isinstance(vec, bytes)
    assert len(np.frombuffer(vec, dtype=np.float32)) == 384
