import argparse
import asyncio
import json
import os
import random
import uuid
import time
from typing import List, Dict, Any

from faker import Faker
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "rag_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

fake = Faker()

async def get_connection():
    return await psycopg.AsyncConnection.connect(DSN, row_factory=dict_row)

async def generate_data(args):
    print(f"Generating dataset with args: {args}")
    
    # Initialize seeds
    random.seed(args.seed)
    Faker.seed(args.seed)
    
    # Generate Documents
    docs = []
    chunks = []
    doc_acls = []
    outbox_events = []
    
    tenant_id = "tenant_1"
    
    print("Generating documents and chunks...")
    for _ in range(args.docs):
        doc_id = str(uuid.uuid4())
        title = fake.sentence()
        # Generate content with multiple paragraphs
        num_chunks = max(1, int(random.gauss(args.avg_chunks, args.avg_chunks * 0.2)))
        
        # Generate raw text chunks
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
            # In a real scenario, we might update title or content.
            # Here, let's simulate updating the last chunk or adding a new one.
            # For simplicity, we just generate a CHUNK_UPSERT event for an existing chunk with new text.
            # Finding a chunk for this doc
            doc_chunks = [c for c in chunks if c['doc_id'] == doc['doc_id']]
            if doc_chunks:
                target_chunk = doc_chunks[-1]
                new_text = fake.paragraph(nb_sentences=5) + " (Updated)"
                target_chunk['chunk_text'] = new_text # Update in memory list too? Not strictly needed for DB insert if we handle conflicts, but here we do batch insert.
                # Actually, if we do batch insert of initial state, updates should probably be separate DB ops or events.
                # But to keep it simple and fast: We will insert the final state of data into DB, 
                # and generate events for the "actions" that happened.
                # WAIT. The outbox pattern implies events drive the indexer.
                # If we insert "updated" state into DB, the events should reflect that.
                
                # Let's append an event.
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
        # We delete from the docs that are NOT updated (to avoid confusion) or just random.
        # Let's just pick random docs.
        docs_to_delete = random.sample(docs, num_deletes)
        for doc in docs_to_delete:
            # Add DELETE event
            # For a document delete, we might need multiple chunk deletes or a doc delete event.
            # The plan says event_type: CHUNK_DELETE.
            # Typically, we'd delete all chunks.
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
            
            # Remove from DB lists (simulating they are gone or marked deleted)
            # But wait, if we insert them and then delete them in same batch... 
            # Ideally, the DB state should reflect the *end* state, OR we insert everything and let the indexer handle it.
            # "Data Generator" usually sets up the initial DB state.
            # If I exclude them from `docs` and `chunks` lists, they won't be in DB.
            # But the events will be in outbox. This is good for testing the "Delete" flow.
            # So: Remove from `docs` and `chunks` lists to be inserted, but keep events?
            # Or insert them, then they get deleted?
            # If the DB doesn't have them, the "DELETE" event might fail if it tries to look them up (depending on consumer logic).
            # Usually, soft delete is used.
            # Let's assume we INSERT everything, and the events tell the indexer what to do.
            # The "Delete Rate" implies these docs *should be deleted*.
            # If I want to test "Processing of Deletes", the DB should probably NOT have them at the end, OR the events trigger removal from Vector DB.
            # Let's assume the DB keeps them (or they are soft deleted) but for this script, I'll just keep them in DB so we can verify they exist before deletion?
            # Actually, standard flow: Data is in Source DB. Event -> Sync to Vector DB.
            # If Source DB deletes data, it sends Event -> Vector DB deletes data.
            # So if I want to simulate "Deleted Docs", I should probably NOT insert them into `documents` table at the end? 
            # OR, I insert them, and then issue a DELETE SQL command?
            # The task says: "Batch Insert ... psycopg ... copy".
            # I will Insert ALL generated docs/chunks into DB (Initial State).
            # Then I will Insert Events.
            # If "Delete Rate" means "These docs are deleted", maybe I should create a separate "Deleted" batch?
            # Let's interpret "Delete Rate" as: generating `CHUNK_DELETE` events for some of the existing docs.
            pass

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
