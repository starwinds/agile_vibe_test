# app/scenarios/data_structures.py

"""
Test Scenario: Common Data Structures

Verifies the functionality of:
- Hash: HSET, HGET, HGETALL
- List: LPUSH, LPOP, LLEN
- Set: SADD, SMEMBERS, SISMEMBER
- Sorted Set: ZADD, ZRANGE

The goal is to ensure these fundamental data structures behave identically
across Redis and Valkey.
"""

def run(client) -> dict:
    """
    Executes the data structures test scenario.

    Args:
        client: A redis.Redis client instance.

    Returns:
        A dictionary containing the scenario name, status, and details.
    """
    scenario_name = "data_structures"
    
    try:
        # === Hash Test ===
        hash_key = f"{scenario_name}_hash"
        client.delete(hash_key)
        client.hset(hash_key, mapping={"field1": "val1", "field2": "val2"})
        hgetall_result = {k.decode(): v.decode() for k, v in client.hgetall(hash_key).items()}
        if hgetall_result != {"field1": "val1", "field2": "val2"}:
            return {"scenario_name": scenario_name, "status": "FAIL", "detail": "HGETALL returned incorrect data."}

        # === List Test ===
        list_key = f"{scenario_name}_list"
        client.delete(list_key)
        client.lpush(list_key, "a", "b", "c")
        if client.llen(list_key) != 3:
            return {"scenario_name": scenario_name, "status": "FAIL", "detail": "LLEN returned incorrect length."}
        lpop_val = client.lpop(list_key).decode()
        if lpop_val != "c":
            return {"scenario_name": scenario_name, "status": "FAIL", "detail": f"LPOP returned '{lpop_val}', expected 'c'."}

        # === Set Test ===
        set_key = f"{scenario_name}_set"
        client.delete(set_key)
        client.sadd(set_key, "a", "b", "c", "a")
        smembers_result = {v.decode() for v in client.smembers(set_key)}
        if smembers_result != {"a", "b", "c"}:
            return {"scenario_name": scenario_name, "status": "FAIL", "detail": "SMEMBERS returned incorrect data."}
        if not client.sismember(set_key, "b"):
            return {"scenario_name": scenario_name, "status": "FAIL", "detail": "SISMEMBER failed for existing member."}

        # === Sorted Set Test ===
        zset_key = f"{scenario_name}_zset"
        client.delete(zset_key)
        client.zadd(zset_key, {"one": 1, "two": 2, "three": 3})
        zrange_result = [v.decode() for v in client.zrange(zset_key, 0, -1)]
        if zrange_result != ["one", "two", "three"]:
            return {"scenario_name": scenario_name, "status": "FAIL", "detail": "ZRANGE returned incorrect order or data."}

        return {
            "scenario_name": scenario_name,
            "status": "OK",
            "detail": "All data structure operations passed."
        }

    except Exception as e:
        return {
            "scenario_name": scenario_name,
            "status": "ERROR",
            "detail": f"An exception occurred: {str(e)}"
        }
