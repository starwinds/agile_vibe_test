import valkey
import struct
import time
import numpy as np

def verify_valkey_vector_search():
    print("--- Starting Valkey Vector Search Verification ---")
    
    # 1. Connect
    try:
        client = valkey.Valkey(host="127.0.0.1", port=6379, decode_responses=False)
        client.ping()
        print("✅ Connected to Valkey Standalone")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    index_name = "verify_idx"
    prefix = "doc_verify:"
    dim = 4
    
    # 2. Cleanup existing
    try:
        client.execute_command("FT.DROPINDEX", index_name)
        print(f"✅ Cleaned up existing index '{index_name}'")
    except Exception:
        pass # Index might not exist

    # 3. Create Index
    try:
        # Schema: id (TAG), vector (VECTOR HNSW)
        client.execute_command(
            "FT.CREATE", index_name, 
            "ON", "HASH", 
            "PREFIX", "1", prefix,
            "SCHEMA", 
            "id", "TAG",
            "vector", "VECTOR", "HNSW", "6", 
                "TYPE", "FLOAT32", 
                "DIM", str(dim), 
                "DISTANCE_METRIC", "L2"
        )
        print(f"✅ Created HNSW index '{index_name}' with DIM={dim}")
    except Exception as e:
        print(f"❌ Index creation failed: {e}")
        return

    # 4. Insert Data
    # Vector 1: [0.1, 0.1, 0.1, 0.1]
    # Vector 2: [0.9, 0.9, 0.9, 0.9]
    vectors = [
        ("1", [0.1, 0.1, 0.1, 0.1]),
        ("2", [0.9, 0.9, 0.9, 0.9])
    ]
    
    try:
        pipe = client.pipeline(transaction=False)
        for doc_id, vec in vectors:
            vec_bytes = struct.pack(f'{len(vec)}f', *vec)
            pipe.hset(f"{prefix}{doc_id}", mapping={
                "id": doc_id,
                "vector": vec_bytes
            })
        pipe.execute()
        print(f"✅ Inserted {len(vectors)} vectors")
    except Exception as e:
        print(f"❌ Insertion failed: {e}")
        return

    # 5. Search
    # Query: [0.1, 0.1, 0.1, 0.1] -> Should match doc 1
    query_vec = [0.1, 0.1, 0.1, 0.1]
    query_bytes = struct.pack(f'{len(query_vec)}f', *query_vec)
    k = 1
    
    print(f"🔍 Searching for nearest neighbor to {query_vec}...")
    
    try:
        # FT.SEARCH verify_idx "*=>[KNN 1 @vector $vec AS score]" PARAMS 2 vec <bytes> DIALECT 2
        query_str = f"*=>[KNN {k} @vector $vec AS score]"
        res = client.execute_command(
            "FT.SEARCH", index_name, 
            query_str, 
            "PARAMS", "2", "vec", query_bytes, 
            "DIALECT", "2"
        )
        
        # Result format: [total_results, key1, [field1, val1, ...], ...]
        total_results = res[0]
        print(f"✅ Search successful. Total results: {total_results}")
        
        if total_results > 0:
            first_doc_key = res[1].decode('utf-8')
            print(f"   Top result key: {first_doc_key}")
            # Verify it matches doc 1
            if first_doc_key == f"{prefix}1":
                 print("✅ Result matches expected document (doc_verify:1)")
            else:
                 print(f"❌ Result mismatch! Expected {prefix}1, got {first_doc_key}")
        else:
            print("❌ No results found")

    except Exception as e:
        print(f"❌ Search failed: {e}")
        return

    print("--- Verification Completed ---")

if __name__ == "__main__":
    verify_valkey_vector_search()
