# app/scenarios/large_payloads.py

"""
Test Scenario: Large Payload Handling

Verifies how Redis and Valkey handle large data payloads.
- Writes and reads payloads of various sizes (e.g., 1MB, 5MB, 10MB).
- Measures latency for SET and GET operations.
- Measures memory consumption for each payload.
"""

import time
import os

def run(client) -> dict:
    """
    Executes the large payload test scenario.

    Args:
        client: A redis.Redis client instance.

    Returns:
        A dictionary containing the scenario name, status, and details.
    """
    scenario_name = "large_payloads"
    key_prefix = f"{{{scenario_name}}}:"
    payload_sizes = {
        "1MB": 1 * 1024 * 1024,
        "5MB": 5 * 1024 * 1024,
        "10MB": 10 * 1024 * 1024,
    }
    
    results = {}
    
    try:
        for name, size in payload_sizes.items():
            print(f"[{scenario_name}] Testing payload size: {name} ({size} bytes)")
            key = f"{key_prefix}{name}"
            
            # Generate a payload of the specified size
            # Using urandom for better randomness, but can be slow.
            # For speed, could use a repeating character pattern.
            payload = os.urandom(size)
            
            # --- 1. Test SET latency and memory ---
            info_before = client.info()
            start_time_set = time.monotonic()
            client.set(key, payload)
            end_time_set = time.monotonic()
            info_after = client.info()

            set_latency = (end_time_set - start_time_set) * 1000  # in ms
            memory_used = info_after["used_memory"] - info_before["used_memory"]
            
            # --- 2. Test GET latency and verify integrity ---
            start_time_get = time.monotonic()
            retrieved_payload = client.get(key)
            end_time_get = time.monotonic()

            get_latency = (end_time_get - start_time_get) * 1000  # in ms
            
            if retrieved_payload != payload:
                raise ValueError(f"Payload mismatch for size {name}")

            results[name] = {
                "set_latency_ms": round(set_latency, 4),
                "get_latency_ms": round(get_latency, 4),
                "memory_bytes": memory_used,
            }
            
            # --- 3. Cleanup ---
            client.delete(key)
            print(f"[{scenario_name}] Test for {name} completed successfully.")

        return {
            "scenario_name": scenario_name,
            "status": "OK",
            "detail": "All large payload tests completed successfully.",
            "metrics": results
        }

    except Exception as e:
        return {
            "scenario_name": scenario_name,
            "status": "ERROR",
            "detail": f"An exception occurred: {str(e)}",
            "metrics": results
        }
    finally:
        # Cleanup any keys that might be left over on error
        for key in client.scan_iter(f"{key_prefix}*"):
            client.delete(key)
