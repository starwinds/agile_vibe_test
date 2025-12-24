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

def test_global_variables_comparison(db_variables):
    """
    Compares all global system variables between MySQL 8.0 and 8.4.
    Identifies variables with different values, and variables unique to each version.
    """
    print("\n--- Comparing ALL global variables ---")
    vars80 = db_variables['mysql80']
    vars84 = db_variables['mysql84']

    diff_values = {}
    unique_to_80 = {}
    unique_to_84 = {}

    # Compare common variables
    for var_name, val80 in vars80.items():
        if var_name in vars84:
            val84 = vars84[var_name]
            if val80 != val84:
                diff_values[var_name] = {'mysql80': val80, 'mysql84': val84}
        else:
            unique_to_80[var_name] = val80
    
    # Find variables unique to 8.4
    for var_name, val84 in vars84.items():
        if var_name not in vars80:
            unique_to_84[var_name] = val84

    report_output = []
    if diff_values:
        report_output.append("\n### Variables with Different Values:")
        report_output.append("| Variable Name | MySQL 8.0 Value | MySQL 8.4 Value |")
        report_output.append("|---------------|-----------------|-----------------|")
        for var_name, values in diff_values.items():
            report_output.append(f"| `{var_name}` | `{values['mysql80']}` | `{values['mysql84']}` |")
    
    if unique_to_80:
        report_output.append("\n### Variables Unique to MySQL 8.0:")
        report_output.append("| Variable Name | MySQL 8.0 Value |")
        report_output.append("|---------------|-----------------|")
        for var_name, value in unique_to_80.items():
            report_output.append(f"| `{var_name}` | `{value}` |")

    if unique_to_84:
        report_output.append("\n### Variables Unique to MySQL 8.4:")
        report_output.append("| Variable Name | MySQL 8.4 Value |")
        report_output.append("|---------------|-----------------|")
        for var_name, value in unique_to_84.items():
            report_output.append(f"| `{var_name}` | `{value}` |")

    if diff_values or unique_to_80 or unique_to_84:
        full_report = "\n".join(report_output)
        print(full_report) # Print to stdout for report generation
        pytest.fail(f"Differences found in global variables. See stdout for details.")
    else:
        print("No differences found in global variables.")