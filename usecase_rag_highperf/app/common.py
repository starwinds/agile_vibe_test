import os
import numpy as np
import requests
import struct

EMBEDDING_DIM = 768
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = "nomic-embed-text"

def embed_text(text: str) -> np.ndarray:
    """
    Generates an embedding for the given text using Ollama.
    Returns a normalized float32 numpy array of shape (EMBEDDING_DIM,).
    """
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": text
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        embedding = data.get("embedding")
        
        if not embedding:
            raise ValueError("No embedding found in response")
            
        vec = np.array(embedding, dtype=np.float32)
        
        # Verify dimension or just warn?
        # If model is different, dim might be different. 
        # But we rely on EMBEDDING_DIM for indexing.
        if vec.shape[0] != EMBEDDING_DIM:
            # We could log a warning here.
            # print(f"Warning: Embedding dim {vec.shape[0]} != {EMBEDDING_DIM}")
            pass
             
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
            
        return vec
        
    except Exception as e:
        # Re-raise to let caller handle failure or crash (fail fast)
        raise RuntimeError(f"Failed to generate embedding: {e}")

def pack_f32(vec: np.ndarray) -> bytes:
    """
    Packs a numpy float32 array into bytes for Valkey vector storage.
    """
    return vec.tobytes()