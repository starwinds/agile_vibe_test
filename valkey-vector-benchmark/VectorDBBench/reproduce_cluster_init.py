from valkey.cluster import ValkeyCluster, ClusterNode
import logging
import sys

# Configure logging to print to stderr
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
# logging.getLogger('valkey').setLevel(logging.DEBUG)

try:
    from valkey import Valkey
    print("Testing basic connection to 127.0.0.1:7000...")
    r = Valkey(host="127.0.0.1", port=7000, decode_responses=True)
    print("Ping:", r.ping())
    print("Cluster Slots:", r.execute_command("CLUSTER SLOTS"))
    
    print(help(ValkeyCluster))
    
    def remap_address(address):
        host, port = address
        mapping = {
            "172.22.0.6": ("127.0.0.1", 7000),
            "172.22.0.5": ("127.0.0.1", 7001),
            "172.22.0.2": ("127.0.0.1", 7002),
            "172.22.0.3": ("127.0.0.1", 7003),
            "172.22.0.7": ("127.0.0.1", 7004),
            "172.22.0.4": ("127.0.0.1", 7005),
        }
        return mapping.get(host, (host, port))

    startup_nodes = [ClusterNode("127.0.0.1", 7000)]
    print(f"Initializing ValkeyCluster with: {startup_nodes}")
    
    client = ValkeyCluster(
        startup_nodes=startup_nodes,
        decode_responses=True,
        password=None,
        address_remap=remap_address
    )
    print("ValkeyCluster initialized successfully.")
    print(client.get_nodes())
except Exception as e:
    print(f"Caught exception: {e}")
    import traceback
    traceback.print_exc()
