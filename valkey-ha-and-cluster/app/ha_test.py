import os
import time
from lib.ha_client import HAClient
from lib import util

# Sentinel and Master configuration
SENTINELS = [("valkey-sentinel1", 26379), ("valkey-sentinel2", 26379), ("valkey-sentinel3", 26379)]
MASTER_NAME = "myvalkey"
TEST_KEY = "ha_test_key"
TEST_VALUE = "hello_ha"

def run_ha_test():
    """Runs the full suite of HA tests."""
    
    util.print_title("Valkey HA (Master-Replica-Sentinel) Test")

    # 1. Initial Connection
    util.print_step("Initializing HAClient")
    try:
        client = HAClient(sentinels=SENTINELS, master_name=MASTER_NAME)
    except Exception as e:
        util.print_fail(f"Could not initialize HAClient: {e}")
        return

    # 2. Basic CRUD Test
    util.print_title("Step 1: Basic CRUD Operations")
    client.set_value(TEST_KEY, TEST_VALUE)
    value_master = client.get_value_from_master(TEST_KEY)
    
    # Allow time for replication
    util.sleep_with_message(2, "Allowing time for replication")
    value_replica = client.get_value_from_replica(TEST_KEY)

    if value_master and value_replica and value_master.decode() == value_replica.decode() == TEST_VALUE:
        util.print_ok("CRUD test passed. Master and replica are in sync.")
    else:
        util.print_fail("CRUD test failed. Data mismatch or read error.")

    # 3. Failover Test
    util.print_title("Step 2: Testing Auto-Failover")
    current_master = client.get_master_address()
    util.print_info(f"Current master is [bold]{current_master}[/bold].")
    
    util.print_step("Simulating master failure by killing the container")
    os.system("docker kill valkey-master")
    util.print_ok("`docker kill valkey-master` command executed.")

    util.sleep_with_message(15, "Waiting for Sentinel to perform failover")

    util.print_step("Attempting to get value after failover")
    try:
        # The client should automatically reconnect to the new master
        new_value = client.get_value_from_master(TEST_KEY)
        new_master = client.get_master_address()

        if new_value and new_value.decode() == TEST_VALUE:
            util.print_ok(f"Successfully read '{TEST_VALUE}' from the new master.")
            util.print_info(f"Failover successful. New master is [bold]{new_master}[/bold].")
        else:
            util.print_fail("Failover test failed. Could not read correct value from new master.")
        
        if current_master == new_master:
            util.print_fail("Failover did not happen. Master address is unchanged.")
        else:
            util.print_ok("Master address has changed, confirming failover.")

    except Exception as e:
        util.print_fail(f"An exception occurred during failover test: {e}")

if __name__ == "__main__":
    run_ha_test()
