from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # 384차원 모델 (VECTOR(384) 권장)

def get_embedding(text: str) -> list[float]:
    """텍스트를 임베딩 벡터로 변환"""
    embedding = model.encode(text)
    return embedding.tolist()
