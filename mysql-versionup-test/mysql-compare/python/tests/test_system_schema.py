import pytest
from common_db import get_db_connection

@pytest.fixture(scope="module")
def system_schemas():
    """
    Fixture to fetch system schema information (tables, columns) from both DBs.
    """
    schemas = {}
    for version in ['mysql80', 'mysql84']:
        conn = None
        try:
            conn = get_db_connection(version)
            if conn:
                cursor = conn.cursor()
                
                # Get all table names from information_schema
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'information_schema';")
                info_schema_tables = {row[0] for row in cursor.fetchall()}
                
                # Get all columns from information_schema
                cursor.execute("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'information_schema';")
                info_schema_columns = {(row[0], row[1]) for row in cursor.fetchall()}

                # Get all table names from mysql db
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'mysql';")
                mysql_db_tables = {row[0] for row in cursor.fetchall()}

                schemas[version] = {
                    "info_schema_tables": info_schema_tables,
                    "info_schema_columns": info_schema_columns,
                    "mysql_db_tables": mysql_db_tables,
                }
            else:
                pytest.fail(f"Could not connect to {version} to fetch schemas.")
        finally:
            if conn:
                conn.close()
    return schemas

def test_information_schema_table_diff(system_schemas):
    """
    Compares the set of tables in information_schema between versions.
    """
    tables80 = system_schemas['mysql80']['info_schema_tables']
    tables84 = system_schemas['mysql84']['info_schema_tables']

    added_in_84 = tables84 - tables80
    removed_from_80 = tables80 - tables84

    print(f"\n--- Comparing information_schema.tables ---")
    if added_in_84:
        print(f"Tables added in 8.4: {sorted(list(added_in_84))}")
    if removed_from_80:
        print(f"Tables removed in 8.4 (were in 8.0): {sorted(list(removed_from_80))}")

    assert not added_in_84 and not removed_from_80, "information_schema.tables differ between versions."

def test_information_schema_column_diff(system_schemas):
    """
    Compares the set of columns in information_schema between versions.
    """
    cols80 = system_schemas['mysql80']['info_schema_columns']
    cols84 = system_schemas['mysql84']['info_schema_columns']

    added_in_84 = cols84 - cols80
    removed_from_80 = cols80 - cols84

    print(f"\n--- Comparing information_schema.columns ---")
    if added_in_84:
        print(f"Columns added in 8.4: {sorted(list(added_in_84))}")
    if removed_from_80:
        print(f"Columns removed in 8.4 (were in 8.0): {sorted(list(removed_from_80))}")

    assert not added_in_84 and not removed_from_80, "information_schema.columns differ between versions."

def test_mysql_db_table_diff(system_schemas):
    """
    Compares the set of tables in the mysql system database between versions.
    """
    tables80 = system_schemas['mysql80']['mysql_db_tables']
    tables84 = system_schemas['mysql84']['mysql_db_tables']

    added_in_84 = tables84 - tables80
    removed_from_80 = tables80 - tables84

    print(f"\n--- Comparing mysql DB tables ---")
    if added_in_84:
        print(f"Tables added in mysql DB in 8.4: {sorted(list(added_in_84))}")
    if removed_from_80:
        print(f"Tables removed from mysql DB in 8.4 (were in 8.0): {sorted(list(removed_from_80))}")

    assert not added_in_84 and not removed_from_80, "mysql DB tables differ between versions."
