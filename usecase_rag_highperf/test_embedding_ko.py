import asyncio
import os
import httpx
import numpy as np
from dotenv import load_dotenv

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = "mxbai-embed-large"

async def get_embedding(text):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": MODEL, "prompt": text},
                timeout=10.0
            )
            resp.raise_for_status()
            emb = resp.json()["embedding"]
            # print(f"Dim: {len(emb)}")
            return emb
        except Exception as e:
            print(f"Error embedding '{text}': {e}")
            return None

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

async def main():
    words = ["사과", "과일", "자동차", "apple", "fruit", "car"]
    embeddings = {}
    
    print(f"Testing model: {MODEL} at {OLLAMA_URL}")
    
    for w in words:
        emb = await get_embedding(w)
        if emb:
            embeddings[w] = emb
        else:
            print(f"Failed to get embedding for {w}")
            return

    pairs = [
        ("사과", "과일"), # Should be high
        ("사과", "자동차"), # Should be low
        ("apple", "fruit"), # Should be high
        ("apple", "car"), # Should be low
        ("사과", "apple"), # Should be high (cross-lingual?)
    ]
    
    print("\nSimilarity Scores:")
    for w1, w2 in pairs:
        sim = cosine_similarity(embeddings[w1], embeddings[w2])
        print(f"{w1} vs {w2}: {sim:.4f}")

if __name__ == "__main__":
    asyncio.run(main())
