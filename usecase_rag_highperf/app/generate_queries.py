import argparse
import asyncio
import json
import os
import random
import re
from typing import List, Dict, Any

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "rag_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def get_connection():
    return await psycopg.AsyncConnection.connect(DSN, row_factory=dict_row)

def extract_keywords(text: str) -> List[str]:
    # Extract capitalized words (excluding start of sentence if possible, but simple regex here)
    # and words > 5 chars.
    words = re.findall(r'\b\w+\b', text)
    keywords = [w for w in words if (w[0].isupper() and len(w) > 1) or len(w) > 5]
    return list(set(keywords))

async def generate_queries(args):
    print(f"Generating queries with args: {args}")
    random.seed(args.seed)
    
    queries = []
    
    async with await get_connection() as aconn:
        async with aconn.cursor() as acur:
            # 1. Fetch random sample of chunks for General strategies
            # We want roughly args.queries queries.
            # We'll fetch a bit more chunks to cover strategies.
            limit = args.queries * 2
            await acur.execute("SELECT chunk_id, doc_id, chunk_text FROM chunks ORDER BY random() LIMIT %s", (limit,))
            chunks = await acur.fetchall()
            
            if not chunks:
                print("No chunks found in DB. Run generate_dataset.py first.")
                return

            # 2. Fetch Fresh chunks from Outbox (for Freshness strategy)
            await acur.execute("""
                SELECT payload 
                FROM outbox_events 
                WHERE event_type = 'CHUNK_UPSERT' 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (int(args.queries * 0.1),))
            fresh_events = await acur.fetchall()
            fresh_chunks = []
            for e in fresh_events:
                p = e['payload']
                if isinstance(p, str):
                    p = json.loads(p)
                fresh_chunks.append(p) # payload has doc_id, chunk_id, text

    print(f"Fetched {len(chunks)} random chunks and {len(fresh_chunks)} fresh events.")
    
    # Generate Queries
    total_needed = args.queries
    generated_count = 0
    
    # Strategy Ratios
    # Semantic: 50%, Keyword: 25%, Hybrid: 20%, Freshness: 5%
    
    counts = {
        "semantic": int(total_needed * 0.5),
        "keyword": int(total_needed * 0.25),
        "hybrid": int(total_needed * 0.20),
        "freshness": int(total_needed * 0.05)
    }
    
    # Fill remaining with Semantic
    counts["semantic"] += total_needed - sum(counts.values())
    
    all_chunks = chunks + fresh_chunks # rough pool
    
    query_id_counter = 1
    
    # Helper to pick a chunk
    def pick_chunk(source_list):
        if not source_list:
            return random.choice(chunks) if chunks else None
        return random.choice(source_list)

    # 1. Freshness
    for _ in range(counts["freshness"]):
        c = pick_chunk(fresh_chunks)
        if not c: continue
        
        # Semantic-like query for fresh doc
        text = c.get('text', c.get('chunk_text', ''))
        sentences = text.split('.')
        q_text = sentences[0] if sentences else text[:50]
        
        queries.append({
            "query_id": f"q{query_id_counter}",
            "type": "freshness",
            "text": q_text.strip(),
            "expected_doc_ids": [c['doc_id']]
        })
        query_id_counter += 1

    # 2. Semantic
    for _ in range(counts["semantic"]):
        c = pick_chunk(chunks)
        if not c: continue
        
        text = c['chunk_text']
        sentences = text.split('.')
        q_text = sentences[0] if sentences else text[:50]
        
        queries.append({
            "query_id": f"q{query_id_counter}",
            "type": "semantic",
            "text": q_text.strip(),
            "expected_doc_ids": [c['doc_id']]
        })
        query_id_counter += 1

    # 3. Keyword
    for _ in range(counts["keyword"]):
        c = pick_chunk(chunks)
        if not c: continue
        
        kw = extract_keywords(c['chunk_text'])
        if not kw:
            kw = c['chunk_text'].split()[:3]
        
        q_text = " ".join(random.sample(kw, min(len(kw), 3)))
        
        queries.append({
            "query_id": f"q{query_id_counter}",
            "type": "keyword",
            "text": q_text.strip(),
            "expected_doc_ids": [c['doc_id']]
        })
        query_id_counter += 1
        
    # 4. Hybrid
    for _ in range(counts["hybrid"]):
        c = pick_chunk(chunks)
        if not c: continue
        
        text = c['chunk_text']
        sentences = text.split('.')
        sem_part = sentences[0] if sentences else text[:20]
        
        kw = extract_keywords(text)
        kw_part = " ".join(random.sample(kw, min(len(kw), 2))) if kw else ""
        
        q_text = f"{sem_part} {kw_part}"
        
        queries.append({
            "query_id": f"q{query_id_counter}",
            "type": "hybrid",
            "text": q_text.strip(),
            "expected_doc_ids": [c['doc_id']]
        })
        query_id_counter += 1

    # Save
    os.makedirs("data", exist_ok=True)
    out_file = "data/queries.jsonl"
    with open(out_file, "w") as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")
            
    print(f"Generated {len(queries)} queries to {out_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate queries for RAG benchmark")
    parser.add_argument("--queries", type=int, default=100, help="Number of queries to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    asyncio.run(generate_queries(args))

if __name__ == "__main__":
    main()
