import os
import sys
import redis
import psycopg
from dotenv import load_dotenv

load_dotenv()

def check_postgres():
    try:
        conn = psycopg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "rag_db"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            connect_timeout=3
        )
        conn.close()
        print("Postgres: OK")
        return True
    except Exception as e:
        print(f"Postgres: FAIL ({e})")
        return False

def check_valkey():
    try:
        r = redis.Redis(
            host=os.getenv("VALKEY_HOST", "localhost"),
            port=int(os.getenv("VALKEY_PORT", 6379)),
            password=os.getenv("VALKEY_PASSWORD", "valkey"),
            socket_timeout=3
        )
        r.ping()
        
        # Check index
        try:
            r.execute_command("FT.INFO", "idx:chunks")
            print("Valkey Index: OK")
        except:
            print("Valkey Index: MISSING (Might need to run indexer)")
            
        print("Valkey: OK")
        return True
    except Exception as e:
        print(f"Valkey: FAIL ({e})")
        return False

if __name__ == "__main__":
    pg_ok = check_postgres()
    vk_ok = check_valkey()
    
    if pg_ok and vk_ok:
        sys.exit(0)
    else:
        sys.exit(1)
