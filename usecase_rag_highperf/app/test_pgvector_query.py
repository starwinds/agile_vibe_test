import asyncio
import os
import psycopg
import numpy as np
from dotenv import load_dotenv

load_dotenv()

async def test_pgvector_query():
    # Setup test data (embedding vector)
    dim = 768
    vec = np.random.rand(dim).astype(np.float32)
    vec = vec / np.linalg.norm(vec) # normalize
    vec_list = vec.tolist()
    
    conn_info = f"host={os.getenv('POSTGRES_HOST', 'localhost')} port={os.getenv('POSTGRES_PORT', 5432)} dbname={os.getenv('POSTGRES_DB', 'rag_db')} user={os.getenv('POSTGRES_USER', 'postgres')} password={os.getenv('POSTGRES_PASSWORD', 'postgres')}"
    
    print("Connecting to Postgres...")
    
    # Case 1: Pass list directly
    print("\nCase 1: Passing list directly...")
    try:
        async with await psycopg.AsyncConnection.connect(conn_info) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT (embedding <=> %s) as distance FROM chunk_embeddings LIMIT 1", (vec_list,))
                print("Case 1 Success!")
    except Exception as e:
        print(f"Case 1 Failed: {e}")

    # Case 2: Pass list with explicit cast ::vector
    print("\nCase 2: Passing list with %s::vector cast...")
    try:
        async with await psycopg.AsyncConnection.connect(conn_info) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT (embedding <=> %s::vector) as distance FROM chunk_embeddings LIMIT 1", (vec_list,))
                print("Case 2 Success!")
    except Exception as e:
        print(f"Case 2 Failed: {e}")

    # Case 3: Pass string representation with cast
    print("\nCase 3: Passing string str(list) with %s::vector cast...")
    try:
        async with await psycopg.AsyncConnection.connect(conn_info) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT (embedding <=> %s::vector) as distance FROM chunk_embeddings LIMIT 1", (str(vec_list),))
                print("Case 3 Success!")
    except Exception as e:
        print(f"Case 3 Failed: {e}")
                
if __name__ == "__main__":
    asyncio.run(test_pgvector_query())