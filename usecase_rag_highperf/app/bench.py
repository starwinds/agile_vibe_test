import argparse
import asyncio
import json
import time
import os
import random
import numpy as np
from typing import List, Dict, Any

import redis.asyncio as redis # Use redis-py async support, it's compatible with Valkey
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

from metrics import MetricsCollector
from common import EMBEDDING_DIM, embed_text, pack_f32

load_dotenv()

# Valkey Config
VALKEY_HOST = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))
VALKEY_PASSWORD = os.getenv("VALKEY_PASSWORD", "valkey")

# Postgres Config
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "rag_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
PG_DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

INDEX_NAME = "idx:chunks"

async def get_pg_connection():
    return await psycopg.AsyncConnection.connect(PG_DSN, row_factory=dict_row)

async def search_valkey(r, vector_bytes: bytes, k: int = 5):
    # FT.SEARCH idx:chunks "*=>[KNN 5 @vector $vec AS score]" PARAMS 2 vec <bytes> DIALECT 2 RETURN 1 doc_id
    query = f"*=>[KNN {k} @vector $vec AS score]"
    try:
        res = await r.execute_command(
            "FT.SEARCH", INDEX_NAME, query,
            "PARAMS", "2", "vec", vector_bytes,
            "DIALECT", "2",
            "RETURN", "1", "doc_id" # Return doc_id only for speed
        )
        # res format: [total_results, key1, extra1, key2, extra2, ...]
        # We just return the raw response or parsed items
        return res
    except Exception as e:
        # print(f"Valkey Search Error: {e}")
        raise e

async def fetch_postgres(ids: List[str]):
    async with await get_pg_connection() as aconn:
        async with aconn.cursor() as acur:
            # ids are like "chunk:uuid", but we want doc_id or chunk_id?
            # The schema says doc_id in Valkey is a TAG.
            # If we returned doc_id, we can query docs.
            # If we returned keys (chunk ids), we can query chunks.
            # Let's assume we want to fetch the CHUNK text from Postgres using the ID derived from Valkey Key.
            # Valkey Key: "chunk:{chunk_id}"
            chunk_ids = [key.split(":")[-1] for key in ids]
            
            await acur.execute("SELECT chunk_text FROM chunks WHERE chunk_id = ANY(%s)", (chunk_ids,))
            return await acur.fetchall()

async def benchmark_query(r, query_item: Dict, mode: str, mock_embedding: bool, collector: MetricsCollector):
    start = time.perf_counter()
    try:
        # 1. Embed
        if mock_embedding:
            # Random vector
            vec = np.random.rand(EMBEDDING_DIM).astype(np.float32)
            # Normalize
            vec /= np.linalg.norm(vec)
            vec_bytes = vec.tobytes()
        else:
            # Real embedding (Slow)
            # Note: common.embed_text is sync. Benchmark should ideally avoid blocking loop.
            # Running in executor?
            loop = asyncio.get_running_loop()
            vec = await loop.run_in_executor(None, embed_text, query_item['text'])
            vec_bytes = pack_f32(vec)

        # 2. Valkey Search
        # Valkey-py execute_command returns a list
        # Response structure: [count, key1, [field1, val1, ...], key2, ...]
        res = await search_valkey(r, vec_bytes, k=5)
        
        # 3. Hybrid Fetch (if enabled)
        if mode == "hybrid_fetch":
            # Parse keys
            # res[0] is count
            # res[1] is key1
            # res[2] is fields (because of RETURN)
            # res[3] is key2 ...
            # We want keys: res[1], res[3], ...
            keys = []
            if res and len(res) > 1:
                # Iterate starting from 1, step 2
                for i in range(1, len(res), 2):
                    keys.append(res[i]) # This is bytes or str depending on decode_responses.
                    # We set decode_responses=False for connection to handle vector bytes input safely?
                    # Or we encode vector param manually.
                    # In `search_valkey`, we passed `vector_bytes`.
                    # If `decode_responses=True`, output is str.
                    # If `decode_responses=False`, output is bytes.
            
            # Convert bytes to str if needed
            keys_str = [k.decode('utf-8') if isinstance(k, bytes) else k for k in keys]
            
            if keys_str:
                await fetch_postgres(keys_str)

        duration = (time.perf_counter() - start) * 1000 # ms
        collector.add_latency(duration)
        
    except Exception as e:
        # print(f"Error processing query: {e}")
        collector.add_error()

async def run_benchmark(args):
    print(f"Starting benchmark: {args.mode}, queries_file={args.queries_file}, mock_emb={args.mock_embedding}")
    
    # Load Queries
    queries = []
    with open(args.queries_file, 'r') as f:
        for line in f:
            queries.append(json.loads(line))
            
    if args.limit and args.limit < len(queries):
        queries = queries[:args.limit]
        
    print(f"Loaded {len(queries)} queries.")

    # Init Redis
    # decode_responses=False is safer for vector bytes input, but then outputs are bytes.
    # Actually redis-py handles bytes input even with decode_responses=True if we pass bytes.
    # But `vec_bytes` is bytes.
    r = redis.Redis(host=VALKEY_HOST, port=VALKEY_PORT, password=VALKEY_PASSWORD, decode_responses=True)

    collector = MetricsCollector()
    collector.start()
    
    # Semaphore for concurrency
    sem = asyncio.Semaphore(args.concurrency)
    
    async def worker(q):
        async with sem:
            await benchmark_query(r, q, args.mode, args.mock_embedding, collector)

    tasks = [worker(q) for q in queries]
    await asyncio.gather(*tasks)
    
    collector.stop()
    await r.aclose()
    
    # Report
    report = collector.calculate_report()
    report["mode"] = args.mode
    report["concurrency"] = args.concurrency
    report["mock_embedding"] = args.mock_embedding
    report["timestamp"] = time.time()
    
    print("\nBenchmark Report:")
    print(json.dumps(report, indent=2))
    
    os.makedirs("out", exist_ok=True)
    outfile = f"out/bench_{args.mode}_{int(report['timestamp'])}.json"
    with open(outfile, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to {outfile}")

def main():
    parser = argparse.ArgumentParser(description="Benchmark RAG components")
    parser.add_argument("--queries-file", default="data/queries.jsonl", help="Path to queries file")
    parser.add_argument("--mode", choices=["valkey_knn", "hybrid_fetch"], default="valkey_knn")
    parser.add_argument("--limit", type=int, help="Limit number of queries to run")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    parser.add_argument("--mock-embedding", action="store_true", default=True, help="Use random vectors instead of real embedding")
    parser.add_argument("--no-mock-embedding", action="store_false", dest="mock_embedding", help="Use real embedding")
    
    args = parser.parse_args()
    
    asyncio.run(run_benchmark(args))

if __name__ == "__main__":
    main()
