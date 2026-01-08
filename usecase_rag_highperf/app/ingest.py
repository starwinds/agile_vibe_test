import os
import hashlib
import json
import psycopg
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# DB Connection
def get_db_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "rag_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        autocommit=False
    )

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Simple overlapping chunking."""
    chunks = []
    start = 0
    text_len = len(text)
    
    if text_len == 0:
        return []

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start += (chunk_size - overlap)
        
    return chunks

def ingest_document(
    tenant_id: str,
    doc_id: str,
    title: str,
    text: str,
    acls: List[Dict[str, str]]
):
    """
    Ingests a document, chunks it, and saves to Postgres with Outbox event.
    acls: List of dicts, e.g., [{"principal": "user:1", "permission": "read"}]
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Upsert Document
            cur.execute("""
                INSERT INTO documents (doc_id, tenant_id, title)
                VALUES (%s, %s, %s)
                ON CONFLICT (doc_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    updated_at = CURRENT_TIMESTAMP
            """, (doc_id, tenant_id, title))

            # 2. Chunking
            chunks = chunk_text(text)
            
            # For this MVP, we are not handling full "update/delete" synchronization 
            # (e.g. deleting old chunks that no longer exist).
            # We just UPSERT new chunks.
            
            for i, chunk_txt in enumerate(chunks):
                chunk_hash = hashlib.sha256(chunk_txt.encode()).hexdigest()
                chunk_id = f"{doc_id}_chunk_{i}"
                
                cur.execute("""
                    INSERT INTO chunks (chunk_id, doc_id, chunk_text, chunk_hash, chunk_index)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        chunk_text = EXCLUDED.chunk_text,
                        chunk_hash = EXCLUDED.chunk_hash,
                        chunk_index = EXCLUDED.chunk_index
                """, (chunk_id, doc_id, chunk_txt, chunk_hash, i))
                
                # Emit Outbox Event
                event_payload = {
                    "type": "CHUNK_UPSERT",
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "chunk_text": chunk_txt,
                    "tenant_id": tenant_id
                }
                
                cur.execute("""
                    INSERT INTO outbox_events (event_type, payload)
                    VALUES (%s, %s)
                """, ("CHUNK_UPSERT", json.dumps(event_payload)))

            # 3. Upsert ACLs
            # Clear old ACLs for simplicity to avoid duplicates/stale data
            cur.execute("DELETE FROM doc_acl WHERE doc_id = %s", (doc_id,))
            for acl in acls:
                cur.execute("""
                    INSERT INTO doc_acl (tenant_id, doc_id, principal, permission)
                    VALUES (%s, %s, %s, %s)
                """, (tenant_id, doc_id, acl['principal'], acl['permission']))

        conn.commit()
        print(f"Successfully ingested document {doc_id} with {len(chunks)} chunks.")
    except Exception as e:
        conn.rollback()
        print(f"Error ingesting document: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Test Run
    sample_text = "Valkey is a high-performance key-value store. It is a fork of Redis. " * 20
    ingest_document(
        tenant_id="tenant_a",
        doc_id="doc_1",
        title="Valkey Intro",
        text=sample_text,
        acls=[{"principal": "user:1", "permission": "read"}]
    )
