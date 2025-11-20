# app/check_memory.py

import redis
from config import TARGETS

def check_baseline_memory():
    print("--- Checking Baseline Memory Usage ---")
    for target_name, conn_params in TARGETS.items():
        try:
            client = redis.Redis(decode_responses=True, **conn_params)
            client.ping()
            print(f"\nConnected to {target_name}.")
            
            # Flush DB to ensure a clean state
            client.flushdb()
            print(f"Database for {target_name} flushed.")
            
            # Get memory info
            memory_info = client.info('memory')
            used_memory = memory_info.get('used_memory', 'N/A')
            used_memory_rss = memory_info.get('used_memory_rss', 'N/A')
            
            print(f"  Used Memory: {used_memory / 1024:.2f} KB")
            print(f"  Used Memory RSS: {used_memory_rss / 1024:.2f} KB")
            
            client.close()
        except redis.exceptions.ConnectionError as e:
            print(f"Error connecting to {target_name}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred for {target_name}: {e}")

if __name__ == "__main__":
    check_baseline_memory()
