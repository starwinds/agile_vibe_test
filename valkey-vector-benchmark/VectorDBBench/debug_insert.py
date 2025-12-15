import valkey
import struct
import time

def test_insert():
    print("Connecting to Valkey...")
    client = valkey.Valkey(host="127.0.0.1", port=6379, decode_responses=True)
    print("Connected.")
    
    print("Creating index...")
    try:
        client.execute_command(
            "FT.CREATE", "debug_idx", "ON", "HASH", "PREFIX", "1", "doc_debug:",
            "SCHEMA", "id", "TAG", "metadata", "NUMERIC", "vector", "VECTOR", "HNSW", "6", "TYPE", "FLOAT32", "DIM", "1536", "DISTANCE_METRIC", "COSINE"
        )
        print("Index created.")
    except Exception as e:
        print(f"Index creation failed (or exists): {e}")

    print("Preparing vector...")
    vector = [0.1] * 1536
    vector_bytes = struct.pack(f'{len(vector)}f', *vector)
    
    print("Inserting 100 vectors with pipeline (batch size 1)...")
    try:
        pipe = client.pipeline(transaction=False)
        for i in range(100):
            pipe.hset(f"doc_debug:{i}", mapping={
                "id": str(i),
                "metadata": i,
                "vector": vector_bytes
            })
            pipe.execute()
            pipe = client.pipeline(transaction=False)
            
        print("Vectors inserted.")
    except Exception as e:
        print(f"Insertion failed: {e}")
        
    print("Cleaning up...")
    try:
        client.execute_command("FT.DROPINDEX", "debug_idx")
        print("Index dropped.")
    except Exception as e:
        print(f"Cleanup failed: {e}")

if __name__ == "__main__":
    test_insert()
