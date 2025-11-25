from rediscluster import RedisCluster
from redis.exceptions import ConnectionError
import backoff
from . import util

class ClusterClient:
    def __init__(self, startup_nodes):
        self.startup_nodes = startup_nodes
        self.client = None
        self.connect()

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=8)
    def connect(self):
        """
        Connects to the Valkey cluster.
        Uses backoff for resilience against temporary unavailability during setup.
        """
        util.print_step("Connecting to Valkey Cluster")
        try:
            self.client = RedisCluster(
                startup_nodes=self.startup_nodes,
                decode_responses=True,
                skip_full_coverage_check=True
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
            # The keys() method in redis-py-cluster returns keys from all nodes
            all_keys = self.client.keys('*')
            
            # This is a simplified way. A more accurate way would be to query each primary.
            # For this test, we'll group by which node the client thinks the key is in.
            node_map = self.client.get_nodes()
            for node in node_map:
                distribution[f"{node.host}:{node.port}"] = 0

            for key in all_keys:
                slot = self.client.keyslot(key)
                # Find which node owns this slot
                for node in node_map:
                    if slot in node.slots:
                        addr = f"{node.host}:{node.port}"
                        if addr in distribution:
                            distribution[addr] += 1
                        else: # Should not happen if map is correct
                            distribution[addr] = 1
                        break
            
            util.print_ok("Successfully retrieved key distribution.")
            return distribution

        except Exception as e:
            util.print_fail(f"Could not get key distribution: {e}")
            return {}
