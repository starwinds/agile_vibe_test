import os
import time
from lib.cluster_client import ClusterClient
from lib import util

# Cluster configuration
STARTUP_NODES = [
    {"host": "localhost", "port": 7000},
    {"host": "localhost", "port": 7001},
    {"host": "localhost", "port": 7002},
]

def run_cluster_test():
    """Runs the full suite of Cluster tests."""

    util.print_title("Valkey Cluster Test")

    # 1. Initial Connection
    util.print_step("Initializing ClusterClient")
    try:
        client = ClusterClient(startup_nodes=STARTUP_NODES)
    except Exception as e:
        util.print_fail(f"Could not initialize ClusterClient: {e}")
        return

    # 2. Key Distribution Test
    util.print_title("Step 1: Key Distribution and Redirection Test")
    util.print_step("Setting 20 keys to observe distribution")
    for i in range(20):
        client.set_value(f"key-{i}", f"value-{i}")
    
    util.print_step("Getting a few keys to test redirection")
    client.get_value("key-5")
    client.get_value("key-15")

    # 3. Check Key Distribution
    util.sleep_with_message(1, "Waiting before checking distribution")
    distribution = client.get_key_distribution()
    if distribution:
        util.print_table(
            "Key Distribution Across Cluster Nodes",
            rows=[(node, count) for node, count in distribution.items()],
            columns=["Node Address", "Key Count"]
        )
    else:
        util.print_fail("Could not retrieve key distribution.")

    # 4. Cluster Failover Test
    util.print_title("Step 2: Testing Cluster Failover")
    # Find a primary node to kill. Let's target the one holding 'key-0'.
    try:
        key0_slot = client.client.keyslot('key-0')
        target_node_info = client.client.get_node_from_slot(key0_slot)
        
        # This gives host and port, but we need the container name.
        # We'll make an assumption based on port.
        target_port = target_node_info['port']
        target_container = f"node-{target_port}"

        util.print_info(f"Key 'key-0' is on node at port {target_port}. Targeting container [bold]{target_container}[/bold] for failure simulation.")

        util.print_step(f"Killing container {target_container}")
        os.system(f"docker kill {target_container}")
        util.print_ok(f"`docker kill {target_container}` executed.")

        util.sleep_with_message(15, "Waiting for cluster to promote a replica")

        util.print_step("Attempting to get 'key-0' after failover")
        value = client.get_value("key-0")

        if value == "value-0":
            util.print_ok("Successfully retrieved 'key-0' after failover. The cluster recovered.")
        else:
            util.print_fail("Failed to retrieve 'key-0' after failover.")

    except Exception as e:
        util.print_fail(f"An error occurred during failover test: {e}")


if __name__ == "__main__":
    run_cluster_test()
