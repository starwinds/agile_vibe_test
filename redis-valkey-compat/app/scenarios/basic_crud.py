# app/scenarios/basic_crud.py

"""
Test Scenario: Basic CRUD Operations

Verifies the functionality of fundamental commands:
- SET: Create a key-value pair.
- GET: Retrieve the value of a key.
- EXISTS: Check if a key exists.
- EXPIRE/TTL: Test key expiration.
- DEL: Delete a key.

The goal is to capture any basic differences in command responses
between Redis and Valkey.
"""

import time

def run(client) -> dict:
    """
    Executes the basic CRUD test scenario.

    Args:
        client: A redis.Redis client instance.

    Returns:
        A dictionary containing the scenario name, status, and details.
    """
    scenario_name = "basic_crud"
    key = f"{scenario_name}_key"
    value = "hello"
    details = []
    
    try:
        # 1. Cleanup: Ensure key doesn't exist before starting
        client.delete(key)
        if client.exists(key):
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": f"Failed to delete key '{key}' during setup."
            }
        details.append("Cleanup OK")

        # 2. SET and GET
        set_result = client.set(key, value)
        get_result = client.get(key)
        
        if not set_result:
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": f"SET command failed for key '{key}'."
            }
        if get_result.decode('utf-8') != value:
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": f"GET command returned unexpected value: got '{get_result.decode('utf-8')}', expected '{value}'."
            }
        details.append("SET/GET OK")

        # 3. EXISTS
        if not client.exists(key):
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": f"EXISTS check failed; key '{key}' should exist but doesn't."
            }
        details.append("EXISTS OK")

        # 4. EXPIRE and TTL
        client.expire(key, 5)
        ttl = client.ttl(key)
        if not (0 < ttl <= 5):
             return {
                "scenario_name": scenario_name,
                "status": "WARN",
                "detail": f"TTL was not in the expected range (1-5s): got {ttl}s."
            }
        time.sleep(6) # Wait for key to expire
        if client.exists(key):
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": f"Key '{key}' did not expire as expected."
            }
        details.append("EXPIRE/TTL OK")

        # 5. DEL
        client.set(key, value) # Re-create the key
        del_count = client.delete(key)
        if del_count != 1:
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": f"DEL command failed to delete key '{key}'."
            }
        if client.exists(key):
            return {
                "scenario_name": scenario_name,
                "status": "FAIL",
                "detail": f"Key '{key}' still exists after DEL."
            }
        details.append("DEL OK")

        return {
            "scenario_name": scenario_name,
            "status": "OK",
            "detail": "All basic CRUD operations passed."
        }

    except Exception as e:
        return {
            "scenario_name": scenario_name,
            "status": "ERROR",
            "detail": f"An exception occurred: {str(e)}"
        }
