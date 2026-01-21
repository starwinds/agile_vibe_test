import argparse
import asyncio
import json
import os
import random
import uuid
import time
import re
from typing import List, Dict, Any

from faker import Faker
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Try importing datasets
try:
    from datasets import load_dataset
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False
    print("Warning: 'datasets' library not found. Falling back to Faker.")

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "rag_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

fake = Faker()

class RealTextGenerator:
    """
    Generates text by sampling from a HuggingFace dataset (e.g. wikitext).
    """
    def __init__(self, dataset_name="wikitext", config="wikitext-2-raw-v1", split="train"):
        global HAS_DATASETS
        if not HAS_DATASETS:
            return
            
        print(f"Loading dataset {dataset_name}/{config}...")
        try:
            self.dataset = load_dataset(dataset_name, config, split=split)
            # Filter extremely short texts (headers etc)
            self.texts = [t for t in self.dataset["text"] if len(t.strip()) > 200]
            print(f"Loaded {len(self.texts)} usable text samples from {dataset_name}.")
        except Exception as e:
            print(f"Failed to load dataset: {e}")
            HAS_DATASETS = False # Fallback

    def sample_text(self, min_length=100) -> str:
        if not HAS_DATASETS or not hasattr(self, 'texts') or not self.texts:
            return fake.paragraph(nb_sentences=5)
        
        # Simple sampling: pick a random text
        # If it's very long, maybe slice it? 
        # Wikitext articles can be long. Let's just pick a chunk.
        text = random.choice(self.texts)
        if len(text) > 2000:
            start = random.randint(0, len(text) - 1000)
            text = text[start:start+1000]
        
        # Cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def sample_title(self) -> str:
        # Generate a title like string
        if not HAS_DATASETS or not hasattr(self, 'texts') or not self.texts:
            return fake.sentence()
        
        # Just grab first few words of a text? Or fake it.
        # Wikitext doesn't have explicit titles in raw config usually (embedded as = Title =).
        # Let's stick to Faker for titles or extract from text.
        return fake.sentence()

async def get_connection():
    return await psycopg.AsyncConnection.connect(DSN, row_factory=dict_row)

async def generate_data(args):
    print(f"Generating dataset with args: {args}")
    
    # Initialize seeds
    random.seed(args.seed)
    Faker.seed(args.seed)
    
    # Initialize Text Generator
    text_gen = RealTextGenerator() if HAS_DATASETS else None
    
    # Generate Documents
    docs = []
    chunks = []
    doc_acls = []
    outbox_events = []
    
    tenant_id = "tenant_1"
    
    print("Generating documents and chunks...")
    for _ in range(args.docs):
        doc_id = str(uuid.uuid4())
        title = text_gen.sample_title() if text_gen else fake.sentence()
        
        # Generate content with multiple paragraphs
        num_chunks = max(1, int(random.gauss(args.avg_chunks, args.avg_chunks * 0.2)))
        
        # Generate raw text chunks
        if text_gen:
             doc_chunks_text = [text_gen.sample_text() for _ in range(num_chunks)]
        else:
             doc_chunks_text = [fake.paragraph(nb_sentences=5) for _ in range(num_chunks)]
        
        docs.append({
            "doc_id": doc_id,
            "tenant_id": tenant_id,
            "title": title,
            "version": 1
        })
        
        # ACL
        doc_acls.append({
            "tenant_id": tenant_id,
            "doc_id": doc_id,
            "principal": "group:public",
            "permission": "read"
        })
        
        # Chunks and Events
        for idx, chunk_text in enumerate(doc_chunks_text):
            chunk_id = str(uuid.uuid4())
            chunks.append({
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "chunk_text": chunk_text,
                "chunk_hash": str(hash(chunk_text)), # Simple hash for demo
                "chunk_index": idx
            })
            
            # Event for UPSERT
            outbox_events.append({
                "event_type": "CHUNK_UPSERT",
                "payload": json.dumps({
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "chunk_text": chunk_text,
                    "tenant_id": tenant_id
                })
            })
            
    # Simulate Updates
    num_updates = int(args.docs * args.update_rate)
    print(f"Generating updates for {num_updates} documents...")
    
    if num_updates > 0 and len(docs) > 0:
        docs_to_update = random.sample(docs, num_updates)
        for doc in docs_to_update:
            doc['version'] += 1
            doc_chunks = [c for c in chunks if c['doc_id'] == doc['doc_id']]
            if doc_chunks:
                target_chunk = doc_chunks[-1]
                if text_gen:
                    new_text = text_gen.sample_text() + " (Updated)"
                else:
                    new_text = fake.paragraph(nb_sentences=5) + " (Updated)"
                    
                target_chunk['chunk_text'] = new_text
                
                outbox_events.append({
                    "event_type": "CHUNK_UPSERT",
                    "payload": json.dumps({
                        "doc_id": doc['doc_id'],
                        "chunk_id": target_chunk['chunk_id'],
                        "chunk_text": new_text,
                        "tenant_id": tenant_id
                    })
                })

    # Simulate Deletes
    num_deletes = int(args.docs * args.delete_rate)
    print(f"Generating deletes for {num_deletes} documents...")
    
    if num_deletes > 0 and len(docs) > 0:
        docs_to_delete = random.sample(docs, num_deletes)
        for doc in docs_to_delete:
            doc_chunks = [c for c in chunks if c['doc_id'] == doc['doc_id']]
            for chunk in doc_chunks:
                outbox_events.append({
                    "event_type": "CHUNK_DELETE",
                    "payload": json.dumps({
                        "doc_id": doc['doc_id'],
                        "chunk_id": chunk['chunk_id'],
                        "tenant_id": tenant_id
                    })
                })

    print(f"Inserting {len(docs)} docs, {len(chunks)} chunks, {len(outbox_events)} events...")

    async with await get_connection() as aconn:
        async with aconn.cursor() as acur:
            # Use copy for speed
            
            # Documents
            print("Copying documents...")
            async with acur.copy("COPY documents (doc_id, tenant_id, title, version) FROM STDIN") as copy:
                for doc in docs:
                    await copy.write_row((doc['doc_id'], doc['tenant_id'], doc['title'], doc['version']))
            
            # Chunks
            print("Copying chunks...")
            async with acur.copy("COPY chunks (chunk_id, doc_id, chunk_text, chunk_hash, chunk_index) FROM STDIN") as copy:
                for chunk in chunks:
                    await copy.write_row((chunk['chunk_id'], chunk['doc_id'], chunk['chunk_text'], chunk['chunk_hash'], chunk['chunk_index']))

            # ACL
            print("Copying doc_acl...")
            async with acur.copy("COPY doc_acl (tenant_id, doc_id, principal, permission) FROM STDIN") as copy:
                for acl in doc_acls:
                    await copy.write_row((acl['tenant_id'], acl['doc_id'], acl['principal'], acl['permission']))

            # Outbox Events
            print("Copying outbox_events...")
            async with acur.copy("COPY outbox_events (event_type, payload) FROM STDIN") as copy:
                for event in outbox_events:
                    await copy.write_row((event['event_type'], event['payload']))
        
        await aconn.commit()

    # Write Manifest
    manifest = {
        "total_docs": len(docs),
        "total_chunks": len(chunks),
        "updated_docs": num_updates,
        "deleted_docs": num_deletes,
        "total_events": len(outbox_events),
        "generated_at": time.time()
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print("Data generation complete. Manifest saved to data/manifest.json")

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic dataset for RAG benchmark")
    parser.add_argument("--docs", type=int, default=1000, help="Number of documents to generate")
    parser.add_argument("--avg-chunks", type=int, default=10, help="Average chunks per document")
    parser.add_argument("--update-rate", type=float, default=0.1, help="Rate of documents to update")
    parser.add_argument("--delete-rate", type=float, default=0.05, help="Rate of documents to delete")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    asyncio.run(generate_data(args))

if __name__ == "__main__":
    main()