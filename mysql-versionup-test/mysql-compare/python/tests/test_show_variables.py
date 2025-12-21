import pytest
from common_db import execute_query, get_db_connection

# Variables to compare as defined in the prompt
VARIABLES_TO_COMPARE = [
    'binlog_expire_logs_seconds',
    'innodb_flush_neighbors',
    'innodb_buffer_pool_in_core_file',
    'innodb_flush_log_at_trx_commit',
    'innodb_log_file_size',
    'gtid_mode',
    'enforce_gtid_consistency',
    'log_bin',
    'binlog_row_image',
]

@pytest.fixture(scope="module")
def db_variables():
    """
    Fixture to fetch all variables from both databases once per module.
    """
    vars_data = {}
    for version in ['mysql80', 'mysql84']:
        conn = None
        try:
            conn = get_db_connection(version)
            if conn:
                all_vars = execute_query(conn, "SHOW VARIABLES;", fetch='all')
                vars_data[version] = {var[0]: var[1] for var in all_vars}
            else:
                pytest.fail(f"Could not connect to {version} to fetch variables.")
        finally:
            if conn:
                conn.close()
    return vars_data

@pytest.mark.parametrize("variable_name", VARIABLES_TO_COMPARE)
def test_variable_comparison(variable_name, db_variables):
    """
    Compares the value of a specific system variable between MySQL 8.0 and 8.4.
    """
    print(f"\n--- Comparing variable: {variable_name} ---")
    
    val80 = db_variables['mysql80'].get(variable_name)
    val84 = db_variables['mysql84'].get(variable_name)

    print(f"[mysql80] {variable_name} = {val80}")
    print(f"[mysql84] {variable_name} = {val84}")

    assert val80 == val84, f"Variable '{variable_name}' differs: 8.0 is '{val80}', 8.4 is '{val84}'"