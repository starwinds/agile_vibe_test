# app/scenarios/memory_eviction.py

"""
Test Scenario: Memory Pressure and Eviction Policy

Verifies how Redis and Valkey handle memory limits and eviction.
- Sets a `maxmemory` limit and `allkeys-lru` eviction policy.
- Fills the memory with keys to trigger eviction.
- Compares the state of the database after eviction.
"""

import time

def run(client) -> dict:
    """
    Executes the memory eviction test scenario.

    Args:
        client: A redis.Redis client instance.

    Returns:
        A dictionary containing the scenario name, status, and details.
    """
    scenario_name = "memory_eviction"
    key_prefix = f"{{{scenario_name}}}:"
    
    original_maxmemory = None
    original_policy = None
    
    try:
        # --- 1. Setup: Get original config and clean slate ---
        original_maxmemory = client.config_get("maxmemory")["maxmemory"]
        original_policy = client.config_get("maxmemory-policy")["maxmemory-policy"]

        # Clean up any old keys from previous runs *before* setting memory limits
        for key in client.scan_iter(f"{key_prefix}*"):
            client.delete(key)
        
        client.config_set("maxmemory", "3mb")
        client.config_set("maxmemory-policy", "allkeys-lru")
        
        # --- 2. Fill memory deterministically ---
        # Add 4MB of data to a 2MB maxmemory instance to ensure eviction is triggered.
        keys_to_add = 40
        payload = "a" * 100_000  # 100KB payload
        
        print(f"[{scenario_name}] Filling memory with {keys_to_add} keys...")
        pipe = client.pipeline(transaction=False)
        for i in range(keys_to_add):
            pipe.set(f"{key_prefix}{i}", payload)
        pipe.execute()
        
        # Give the server a moment to process evictions
        time.sleep(0.1)

        # --- 3. Collect results after eviction ---
        keys_after = len(list(client.scan_iter(f"{key_prefix}*")))
        evicted_count = keys_to_add - keys_after
        
        print(f"[{scenario_name}] Keys added: {keys_to_add}, Keys remaining: {keys_after}")

        if evicted_count <= 0:
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": "Eviction did not occur as expected. The number of keys did not decrease.",
                "metrics": {
                    "keys_before": keys_to_add,
                    "keys_after": keys_after,
                    "evicted_count": evicted_count,
                }
            }

        return {
            "scenario_name": scenario_name,
            "status": "OK",
            "detail": f"Evicted {evicted_count} keys successfully.",
            "metrics": {
                "keys_before": keys_to_add,
                "keys_after": keys_after,
                "evicted_count": evicted_count,
            }
        }

    except Exception as e:
        return {
            "scenario_name": scenario_name,
            "status": "ERROR",
            "detail": f"An exception occurred: {str(e)}",
            "metrics": {}
        }
    finally:
        # --- 4. Teardown: Restore original config ---
        # CRITICAL: Clean up keys *first* to release memory,
        # otherwise restoring maxmemory might fail.
        for key in client.scan_iter(f"{key_prefix}*"):
            client.delete(key)
        
        if original_maxmemory is not None:
            client.config_set("maxmemory", original_maxmemory)
        if original_policy is not None:
            client.config_set("maxmemory-policy", original_policy)
