import redis.sentinel
import backoff
from . import util

class HAClient:
    def __init__(self, sentinels, master_name):
        self.sentinels = sentinels
        self.master_name = master_name
        self.sentinel = redis.sentinel.Sentinel(self.sentinels, socket_timeout=0.5)
        self.master = None
        self.replica = None
        self.connect()

    @backoff.on_exception(backoff.expo, redis.exceptions.ConnectionError, max_tries=8)
    def connect(self):
        """
        Connects to the master and replica using Sentinel discovery.
        Uses backoff for resilience.
        """
        util.print_step("Discovering master and replica using Sentinel")
        try:
            self.master = self.sentinel.master_for(self.master_name, socket_timeout=0.5)
            self.replica = self.sentinel.slave_for(self.master_name, socket_timeout=0.5)
            util.print_ok(f"Discovered Master: {self.get_master_address()}")
            util.print_ok(f"Discovered Replica: {self.get_replica_address()}")
        except redis.exceptions.MasterNotFoundError:
            util.print_fail("Master not found by Sentinel.")
            raise
        except redis.exceptions.ConnectionError as e:
            util.print_fail(f"Connection failed: {e}")
            raise

    def get_master_address(self):
        """Returns the address of the current master."""
        if self.master:
            return f"{self.master.connection_pool.connection_kwargs['host']}:{self.master.connection_pool.connection_kwargs['port']}"
        return "N/A"

    def get_replica_address(self):
        """Returns the address of a replica."""
        if self.replica:
            return f"{self.replica.connection_pool.connection_kwargs['host']}:{self.replica.connection_pool.connection_kwargs['port']}"
        return "N/A"

    @backoff.on_exception(backoff.expo, redis.exceptions.ConnectionError, max_tries=5)
    def set_value(self, key, value):
        """Sets a value on the master."""
        util.print_step(f"Setting key '{key}' to '{value}' on master")
        try:
            self.master.set(key, value)
            util.print_ok(f"Successfully set '{key}'.")
        except redis.exceptions.ConnectionError as e:
            util.print_fail(f"Failed to set '{key}': {e}")
            self.connect() # Re-discover master and retry
            self.master.set(key, value)
            util.print_ok(f"Successfully set '{key}' after reconnect.")


    @backoff.on_exception(backoff.expo, redis.exceptions.ConnectionError, max_tries=5)
    def get_value_from_master(self, key):
        """Gets a value from the master."""
        util.print_step(f"Getting key '{key}' from master")
        try:
            value = self.master.get(key)
            if value:
                util.print_ok(f"Got value '{value.decode()}' from master.")
            else:
                util.print_fail(f"Key '{key}' not found on master.")
            return value
        except redis.exceptions.ConnectionError as e:
            util.print_fail(f"Failed to get '{key}' from master: {e}")
            self.connect() # Re-discover master and retry
            value = self.master.get(key)
            util.print_ok(f"Got value '{value.decode()}' from master after reconnect.")
            return value

    @backoff.on_exception(backoff.expo, redis.exceptions.ConnectionError, max_tries=5)
    def get_value_from_replica(self, key):
        """Gets a value from the replica."""
        util.print_step(f"Getting key '{key}' from replica")
        try:
            value = self.replica.get(key)
            if value:
                util.print_ok(f"Got value '{value.decode()}' from replica.")
            else:
                util.print_fail(f"Key '{key}' not found on replica.")
            return value
        except redis.exceptions.ConnectionError as e:
            util.print_fail(f"Failed to get '{key}' from replica: {e}")
            self.connect() # Re-discover replica and retry
            value = self.replica.get(key)
            util.print_ok(f"Got value '{value.decode()}' from replica after reconnect.")
            return value
