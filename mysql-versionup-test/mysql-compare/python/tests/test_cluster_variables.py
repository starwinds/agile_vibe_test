import pytest
import sys
import os

# Ensure we can import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from common_db import get_cluster_primary, get_db_connection
    from config import CLUSTER_CONFIGS
except ImportError:
    # This is expected during the "Red" phase of TDD
    pass

@pytest.mark.cluster
def test_cluster_primary_identification():
    """
    Test that we can identify the Primary node in the InnoDB Cluster.
    """
    # 1. 8.0 Cluster
    # We pass the list of potential nodes. 
    # In a real scenario, we might try connecting to any of them to find the topology.
    primary_80_info = get_cluster_primary(CLUSTER_CONFIGS['mysql80'])
    assert primary_80_info is not None, "Could not identify MySQL 8.0 Cluster Primary"
    print(f"Found 8.0 Primary: {primary_80_info['host']}:{primary_80_info['port']}")

    # 2. 8.4 Cluster
    primary_84_info = get_cluster_primary(CLUSTER_CONFIGS['mysql84'])
    assert primary_84_info is not None, "Could not identify MySQL 8.4 Cluster Primary"
    print(f"Found 8.4 Primary: {primary_84_info['host']}:{primary_84_info['port']}")

@pytest.mark.cluster
def test_compare_cluster_global_variables():
    """
    Compare GLOBAL VARIABLES between MySQL 8.0 Primary and MySQL 8.4 Primary.
    """
    # Get Primaries
    primary_80 = get_cluster_primary(CLUSTER_CONFIGS['mysql80'])
    primary_84 = get_cluster_primary(CLUSTER_CONFIGS['mysql84'])
    
    assert primary_80, "8.0 Primary not found"
    assert primary_84, "8.4 Primary not found"

    # Connect and get variables
    conn80 = get_db_connection(primary_80)
    conn84 = get_db_connection(primary_84)

    assert conn80, "Could not connect to 8.0 Primary"
    assert conn84, "Could not connect to 8.4 Primary"

    cursor80 = conn80.cursor()
    cursor80.execute("SHOW GLOBAL VARIABLES")
    vars80 = dict(cursor80.fetchall())

    cursor84 = conn84.cursor()
    cursor84.execute("SHOW GLOBAL VARIABLES")
    vars84 = dict(cursor84.fetchall())
    
    conn80.close()
    conn84.close()

    # Compare
    diff_values = {}
    only_in_80 = []
    only_in_84 = []

    all_keys = set(vars80.keys()) | set(vars84.keys())

    for key in all_keys:
        val80 = vars80.get(key)
        val84 = vars84.get(key)
        
        if key not in vars80:
            only_in_84.append(key)
        elif key not in vars84:
            only_in_80.append(key)
        elif val80 != val84:
            diff_values[key] = {
                "mysql80": val80,
                "mysql84": val84
            }

    # Save results to JSON for reporting
    import json
    import os
    
    result_data = {
        "timestamp": "now", # Placeholder, use datetime in real app or just skip
        "summary": {
            "total_in_80": len(vars80),
            "total_in_84": len(vars84),
            "different_values": len(diff_values),
            "only_in_80": len(only_in_80),
            "only_in_84": len(only_in_84)
        },
        "different_values": diff_values,
        "only_in_80": sorted(only_in_80),
        "only_in_84": sorted(only_in_84)
    }
    
    json_path = os.path.join(os.path.dirname(__file__), '../cluster_variable_comparison.json')
    with open(json_path, 'w') as f:
        json.dump(result_data, f, indent=4)
        
    print(f"Cluster variable comparison saved to {json_path}")

    # Naive comparison for assertion
    assert len(vars80) > 0
    assert len(vars84) > 0
