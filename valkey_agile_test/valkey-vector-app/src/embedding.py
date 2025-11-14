from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")  # 384차원 모델

def get_embedding(text: str) -> bytes:
    embedding = model.encode(text)
    return np.array(embedding, dtype=np.float32).tobytes()
