# app/scenarios/scan_and_iter.py

"""
Test Scenario: Scanning and Iteration

Verifies the functionality of iteration commands:
- SCAN: Iterates the key space.
- HSCAN: Iterates fields of a Hash.
- ZSCAN: Iterates elements of a Sorted Set.

The goal is to detect differences in cursor behavior, returned data,
and iteration completion. Note that the order of elements returned
by SCAN is not guaranteed, so this test focuses on completeness.
"""

def run(client) -> dict:
    """
    Executes the scan and iteration test scenario.

    Args:
        client: A redis.Redis client instance.

    Returns:
        A dictionary containing the scenario name, status, and details.
    """
    scenario_name = "scan_and_iter"
    
    try:
        # === SCAN Test ===
        scan_prefix = f"{{{scenario_name}}}:"
        expected_keys = {f"{scan_prefix}{i}".encode() for i in range(100)}
        
        # Clean up previous keys and populate
        pipe = client.pipeline()
        for key in client.scan_iter(f"{scan_prefix}*"):
            pipe.delete(key)
        pipe.execute()
        
        for key in expected_keys:
            pipe.set(key, "val")
        pipe.execute()

        # Perform SCAN and collect keys
        found_keys = set()
        for key in client.scan_iter(f"{scan_prefix}*"):
            found_keys.add(key)
        
        if found_keys != expected_keys:
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": f"SCAN did not return the complete set of keys. Missing: {len(expected_keys - found_keys)}, Extra: {len(found_keys - expected_keys)}"
            }

        # === HSCAN Test ===
        hash_key = f"{scenario_name}_hash"
        expected_hash = {f"field{i}": f"val{i}" for i in range(50)}
        client.delete(hash_key)
        client.hset(hash_key, mapping=expected_hash)
        
        found_hash = {}
        for field, value in client.hscan_iter(hash_key):
            found_hash[field.decode()] = value.decode()
            
        if found_hash != expected_hash:
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": "HSCAN did not return the complete hash contents."
            }

        # === ZSCAN Test ===
        zset_key = f"{scenario_name}_zset"
        expected_zset = {f"member{i}": float(i) for i in range(50)}
        client.delete(zset_key)
        client.zadd(zset_key, mapping=expected_zset)
        
        found_zset = {}
        for member, score in client.zscan_iter(zset_key):
            found_zset[member.decode()] = score
            
        if found_zset != expected_zset:
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": "ZSCAN did not return the complete sorted set contents."
            }

        return {
            "scenario_name": scenario_name,
            "status": "OK",
            "detail": "SCAN, HSCAN, and ZSCAN iterations completed successfully."
        }

    except Exception as e:
        return {
            "scenario_name": scenario_name,
            "status": "ERROR",
            "detail": f"An exception occurred: {str(e)}"
        }
