import os
import numpy as np
import requests
import struct

EMBEDDING_DIM = 1024
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = "mxbai-embed-large"

def embed_text(text: str, task_type: str = "search_document") -> np.ndarray:
    """
    Generates an embedding for the given text using Ollama.
    Returns a normalized float32 numpy array of shape (EMBEDDING_DIM,).
    
    Args:
        text: The text to embed.
        task_type: 'search_document' for indexing, 'search_query' for search. 
                   If OLLAMA_MODEL starts with 'nomic', appropriate prefix is added.
    """
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    
    # Handle task prefix for nomic-embed-text
    if OLLAMA_MODEL.startswith("nomic"):
        if task_type == "search_document" and not text.startswith("search_document:"):
            text = f"search_document: {text}"
        elif task_type == "search_query" and not text.startswith("search_query:"):
            text = f"search_query: {text}"

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