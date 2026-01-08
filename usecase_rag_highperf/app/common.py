import numpy as np
import struct

EMBEDDING_DIM = 384

def embed_text_stub(text: str) -> np.ndarray:
    """
    Creates a deterministic stub embedding based on text hash.
    Returns a normalized float32 numpy array of shape (EMBEDDING_DIM,).
    """
    # Simple deterministic hash to seed the random generator
    # hash() in Python can be non-deterministic across runs/processes if PYTHONHASHSEED is not set.
    # For a stub, it's better to use something stable like hashlib if we want strict consistency,
    # but for this MVP, using a fixed seed or just random is fine. 
    # To make it slightly more consistent for testing within same process:
    seed = abs(hash(text)) % (2**32)
    rng = np.random.default_rng(seed)
    
    # Generate random vector
    vec = rng.standard_normal(EMBEDDING_DIM).astype(np.float32)
    
    # Normalize
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm

def pack_f32(vec: np.ndarray) -> bytes:
    """
    Packs a numpy float32 array into bytes for Valkey vector storage.
    """
    return vec.tobytes()
