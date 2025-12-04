import os
import time
import json
import subprocess
from lib.cluster_client import ClusterClient
from lib import util

# Cluster configuration
STARTUP_NODES = [
    {"host": "node-7000", "port": 6379},
    {"host": "node-7001", "port": 6379},
    {"host": "node-7002", "port": 6379},
]

def run_cluster_test():
    """Runs the full suite of Cluster tests."""

    util.print_title("Valkey Cluster Test")

    # 1. Initial Connection
    util.print_step("Initializing ClusterClient")
    try:
        client = ClusterClient(startup_nodes=STARTUP_NODES, cluster_error_retry_attempts=3)
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
        target_node_info = client.client.nodes_manager.get_node_from_slot(key0_slot)
        
        # This gives host and port. Host is likely an IP.
        # We need to find the container name from this IP to kill it.
        target_ip = target_node_info.host
        target_port = target_node_info.port
        
        util.print_info(f"Target node IP: {target_ip}, Port: {target_port}")
        
        target_container = None
        try:
            cmd = "docker network inspect valkey-ha-and-cluster_valkey-cluster-net"
            result = subprocess.check_output(cmd, shell=True)
            network_data = json.loads(result)
            for container_id, container in network_data[0]['Containers'].items():
                if container['IPv4Address'].split('/')[0] == target_ip:
                    target_container = container['Name']
                    break
        except Exception as e:
             util.print_fail(f"Failed to inspect docker network: {e}")

        if not target_container:
             # Fallback or error
             target_container = f"node-{target_port}" # This was the old assumption
             util.print_fail(f"Could not resolve container name for IP {target_ip}. Trying fallback {target_container}")

        util.print_info(f"Key 'key-0' is on node {target_ip}:{target_port}. Targeting container [bold]{target_container}[/bold] for failure simulation.")

        util.print_step(f"Killing container {target_container}")
        os.system(f"docker kill {target_container}")
        util.print_ok(f"`docker kill {target_container}` executed.")

        util.sleep_with_message(30, "Waiting for cluster to promote a replica")

        # util.print_step("Re-initializing client to verify cluster recovery")
        # try:
        #     client = ClusterClient(startup_nodes=STARTUP_NODES)
        # except Exception as e:
        #     util.print_fail(f"Could not re-initialize ClusterClient: {e}")
        #     return

        util.print_step("Attempting to get 'key-0' after failover (expecting auto-recovery)")
        
        # Retry loop for failover recovery
        max_retries = 20
        for attempt in range(max_retries):
            try:
                value = client.get_value("key-0")
                if value == "value-0":
                    util.print_ok("Successfully retrieved 'key-0' after failover. The cluster recovered.")
                    break
                else:
                    util.print_info(f"Attempt {attempt+1}/{max_retries}: Got unexpected value '{value}'. Retrying in 5s...")
            except Exception as e:
                util.print_info(f"Attempt {attempt+1}/{max_retries}: Error retrieving key ({e}). Retrying in 5s...")
            
            time.sleep(5)
        else:
            util.print_fail("Failed to retrieve 'key-0' after failover.")

    except Exception as e:
        util.print_fail(f"An error occurred during failover test: {e}")


if __name__ == "__main__":
    run_cluster_test()
