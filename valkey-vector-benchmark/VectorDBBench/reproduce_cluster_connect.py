from valkey import ValkeyCluster
from valkey.exceptions import ValkeyClusterException

startup_nodes = [
    {"host": "127.0.0.1", "port": "7000"},
]

try:
    vc = ValkeyCluster(startup_nodes=startup_nodes, require_full_coverage=False)
    print("Cluster initialized successfully")
    print("Nodes:", vc.get_nodes())
    print("Cluster info:", vc.cluster_info())
except Exception as e:
    print(f"Failed to connect: {e}")
