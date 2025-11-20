# app/scenarios/lua_and_tx.py

"""
Test Scenario: Lua Scripting and Transactions

Verifies the functionality of:
- EVAL / EVALSHA: Lua script execution.
- MULTI / EXEC: Atomic transaction blocks.

The goal is to check for behavioral differences in server-side scripting
and transaction handling between Redis and Valkey.
"""

def run(client) -> dict:
    """
    Executes the Lua and transaction test scenario.

    Args:
        client: A redis.Redis client instance.

    Returns:
        A dictionary containing the scenario name, status, and details.
    """
    scenario_name = "lua_and_tx"
    
    try:
        # === Lua Script Test (EVAL) ===
        lua_script = "return redis.call('SET', KEYS[1], ARGV[1])"
        key = f"{scenario_name}_lua_key"
        value = "lua_value"
        client.delete(key)
        
        client.eval(lua_script, 1, key, value)
        if client.get(key).decode() != value:
            return {"scenario_name": scenario_name, "status": "FAIL", "detail": "EVAL script to SET key failed."}

        # === Lua Script Test (EVALSHA) ===
        sha1 = client.script_load(lua_script)
        client.delete(key)
        client.evalsha(sha1, 1, key, "evalsha_value")
        if client.get(key).decode() != "evalsha_value":
            return {"scenario_name": scenario_name, "status": "FAIL", "detail": "EVALSHA script failed."}

        # === Transaction Test (MULTI/EXEC) ===
        tx_key1 = f"{scenario_name}_tx_key1"
        tx_key2 = f"{scenario_name}_tx_key2"
        client.delete(tx_key1, tx_key2)

        pipe = client.pipeline()
        pipe.multi()
        pipe.set(tx_key1, "1")
        pipe.incr(tx_key1)
        pipe.set(tx_key2, "2")
        results = pipe.execute()

        if not all(results):
             return {"scenario_name": scenario_name, "status": "FAIL", "detail": f"Transaction command failed: {results}"}

        if client.get(tx_key1).decode() != "2" or client.get(tx_key2).decode() != "2":
            return {"scenario_name": scenario_name, "status": "FAIL", "detail": "Transaction did not execute atomically or correctly."}

        return {
            "scenario_name": scenario_name,
            "status": "OK",
            "detail": "Lua scripts and transactions executed successfully."
        }

    except Exception as e:
        return {
            "scenario_name": scenario_name,
            "status": "ERROR",
            "detail": f"An exception occurred: {str(e)}"
        }
