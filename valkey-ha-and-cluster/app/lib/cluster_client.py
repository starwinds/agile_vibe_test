from redis.cluster import RedisCluster, ClusterNode
from redis.exceptions import ConnectionError
import backoff
from . import util

class ClusterClient:
    def __init__(self, startup_nodes, **kwargs):
        self.startup_nodes = startup_nodes
        self.client = None
        self.connect(**kwargs)

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=8)
    def connect(self, **kwargs):
        """
        Connects to the Valkey cluster.
        Uses backoff for resilience against temporary unavailability during setup.
        """
        util.print_step("Connecting to Valkey Cluster")
        try:
            # redis-py requires startup_nodes to be ClusterNode objects or similar
            # It can also take a list of dicts if formatted correctly, but let's be explicit if needed.
            # actually redis-py RedisCluster startup_nodes arg expects ClusterNode objects
            # OR a list of dicts with 'host' and 'port'.
            # Let's try passing the list of dicts directly as it matches the signature mostly,
            # but we need to be careful about the arguments.
            
            # Convert dicts to ClusterNode if needed, or just pass host/port.
            # redis-py RedisCluster init:
            # __init__(self, host: Optional[str] = None, port: int = 6379, startup_nodes: Optional[List[ClusterNode]] = None, ...)
            
            nodes = [ClusterNode(n['host'], n['port']) for n in self.startup_nodes]

            self.client = RedisCluster(
                startup_nodes=nodes,
                decode_responses=True,
                **kwargs
            )
            # Check connection
            self.client.ping()
            util.print_ok("Successfully connected to the cluster.")
        except ConnectionError as e:
            util.print_fail(f"Failed to connect to cluster: {e}")
            raise

    def set_value(self, key, value):
        """Sets a value in the cluster."""
        util.print_step(f"Setting key '{key}' to '{value}'")
        try:
            self.client.set(key, value)
            util.print_ok(f"Successfully set '{key}'.")
        except Exception as e:
            util.print_fail(f"Failed to set '{key}': {e}")

    def get_value(self, key):
        """Gets a value from the cluster."""
        util.print_step(f"Getting key '{key}'")
        try:
            value = self.client.get(key)
            if value is not None:
                util.print_ok(f"Got value '{value}' for key '{key}'.")
            else:
                util.print_fail(f"Key '{key}' not found.")
            return value
        except Exception as e:
            util.print_fail(f"Failed to get '{key}': {e}")
            return None

    def get_key_distribution(self):
        """
        Gets the distribution of keys across the cluster nodes.
        Returns a dictionary with node address as key and key count as value.
        """
        util.print_step("Getting key distribution across cluster nodes")
        try:
            distribution = {}
            # Use scan_iter to ensure we get keys from all nodes
            all_keys = list(self.client.scan_iter(match='*'))
            
            # This is a simplified way. A more accurate way would be to query each primary.
            # For this test, we'll group by which node the client thinks the key is in.
            # redis-py's get_nodes() returns a list of ClusterNode objects
            nodes = self.client.get_nodes()
            
            for node in nodes:
                distribution[f"{node.host}:{node.port}"] = 0

            for key in all_keys:
                # keyslot() is available on the cluster client
                slot = self.client.keyslot(key)
                
                # get_node_from_slot is available via nodes_manager in redis-py
                owner_node = self.client.nodes_manager.get_node_from_slot(slot)
                
                if owner_node:
                     addr = f"{owner_node.host}:{owner_node.port}"
                     if addr in distribution:
                         distribution[addr] += 1
                     else:
                         distribution[addr] = 1
                
            util.print_ok("Successfully retrieved key distribution.")
            return distribution

        except Exception as e:
            util.print_fail(f"Could not get key distribution: {e}")
            return {}


