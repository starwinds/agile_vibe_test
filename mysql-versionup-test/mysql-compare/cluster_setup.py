# This script is intended to be run via mysqlsh
# Usage: docker exec -it cluster-setup mysqlsh --py --file /script/cluster_setup.py

import time

def setup_cluster(version, node_names, cluster_name):
    print(f"\n=== Setting up cluster for {version} ===")
    primary = node_names[0]
    others = node_names[1:]
    
    uri_primary = f"root:rootpassword@{primary}:3306"
    
    print(f"Connecting to Primary: {uri_primary}")
    try:
        # Connect to the primary node
        shell.connect(uri_primary)
    except Exception as e:
        print(f"CRITICAL: Failed to connect to {primary}. Ensure the container is healthy.")
        print(e)
        return

    # Create Cluster
    try:
        print(f"Creating cluster '{cluster_name}' on {primary}...")
        # Check if cluster already exists
        try:
            cluster = dba.get_cluster(cluster_name)
            print(f"Cluster '{cluster_name}' already exists.")
        except:
            cluster = dba.create_cluster(cluster_name)
            print(f"Cluster '{cluster_name}' created successfully.")
    except Exception as e:
        print(f"Error creating cluster: {e}")
        return

    # Add instances
    for node in others:
        uri_node = f"root:rootpassword@{node}:3306"
        print(f"Adding instance {node}...")
        try:
            # Check if already in cluster
            status = cluster.status()
            already_member = False
            # Simple check in topology (this is a rough check, status returns a dictionary)
            # We'll just try to add and catch error if it's already there
            cluster.add_instance(uri_node, {"recoveryMethod": "clone", "memberSslMode": "REQUIRED"}) 
            # Note: memberSslMode might be needed depending on config, but clone is key.
            print(f"Successfully added {node}.")
        except Exception as e:
            if "already a member" in str(e):
                 print(f"{node} is already a member.")
            else:
                print(f"Error adding {node}: {e}")

    print(f"\n--- Cluster {cluster_name} Status ---")
    try:
        print(cluster.status())
    except:
        pass

# Wait a bit for containers to be fully ready if this script is run immediately
# print("Waiting 10s for network/db stability...")
# time.sleep(10)

# Setup 8.0
setup_cluster("MySQL 8.0", ["mysql80-1", "mysql80-2", "mysql80-3"], "cluster80")

# Setup 8.4
setup_cluster("MySQL 8.4", ["mysql84-1", "mysql84-2", "mysql84-3"], "cluster84")
