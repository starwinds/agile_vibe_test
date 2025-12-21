import pytest
from common_db import execute_query

def test_pk_less_table(db_connection):
    """
    Tests behavior of creating tables without a Primary Key.
    """
    conn, version = db_connection
    print(f"\n--- [{version}] Testing creation of PK-less table ---")
    
    error = None
    try:
        # Create table without PK
        execute_query(conn, "CREATE TABLE pk_less (id INT, data VARCHAR(100)) ENGINE=InnoDB;")
        
        # Verify table was created
        res = execute_query(conn, "SHOW TABLES LIKE 'pk_less';", fetch='one')
        assert res is not None, "PK-less table was not created."
        print(f"[{version}] Result: PK-less table created successfully.")

        # Try to add a secondary index
        execute_query(conn, "CREATE INDEX idx_data ON pk_less(data);")
        
        # Verify index was created
        res = execute_query(conn, "SHOW INDEX FROM pk_less WHERE Key_name = 'idx_data';", fetch='one')
        assert res is not None, "Secondary index on PK-less table was not created."
        print(f"[{version}] Result: Secondary index on PK-less table created successfully.")

    except Exception as e:
        error = e

    if error:
        pytest.fail(f"[{version}] Operations on PK-less table failed unexpectedly: {error}")
    else:
        assert True

def test_collation_join(db_connection):
    """
    Tests behavior of JOINing tables with different collations.
    This is expected to fail without explicit collation casting.
    """
    conn, version = db_connection
    print(f"\n--- [{version}] Testing JOIN on different collations ---")
    
    error = None
    try:
        # Create two tables with different collations
        execute_query(conn, "CREATE TABLE table_general (id INT, name VARCHAR(50)) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
        execute_query(conn, "CREATE TABLE table_ai_ci (id INT, name VARCHAR(50)) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;")

        # Insert data
        execute_query(conn, "INSERT INTO table_general VALUES (1, 'test');")
        execute_query(conn, "INSERT INTO table_ai_ci VALUES (1, 'test');")

        # Perform the JOIN
        query = "SELECT * FROM table_general tg JOIN table_ai_ci tai ON tg.name = tai.name;"
        execute_query(conn, query, fetch='all')

    except Exception as e:
        error = e

    if error:
        print(f"[{version}] Result: JOIN on different collations FAILED as expected.")
        print(f"[{version}] Error Code: {error.errno}, Msg: {error.msg}")
        assert 'Illegal mix of collations' in error.msg
    else:
        pytest.fail(f"[{version}] JOIN on different collations succeeded unexpectedly.")


def test_new_reserved_word(db_connection):
    """
    Tests behavior of a new reserved word in 8.4 ('QUALIFY').
    """
    conn, version = db_connection
    word = "QUALIFY"
    print(f"\n--- [{version}] Testing new reserved word: {word} ---")
    
    error = None
    try:
        execute_query(conn, f"CREATE TABLE {word} (id INT);")
    except Exception as e:
        error = e

    if version == 'mysql80':
        if error:
            pytest.fail(f"[{version}] DDL with word '{word}' failed unexpectedly: {error}")
        else:
            print(f"[{version}] Result: DDL with word '{word}' SUCCEEDED as expected.")
            assert True
    elif version == 'mysql84':
        if error:
            print(f"[{version}] Result: DDL with word '{word}' FAILED as expected.")
            assert True # Just check that it failed
        else:
            pytest.fail(f"[{version}] DDL with word '{word}' succeeded unexpectedly.")

def test_removed_reserved_word(db_connection):
    """
    Tests behavior of a removed reserved word in 8.4 ('MASTER_BIND').
    """
    conn, version = db_connection
    word = "MASTER_BIND"
    print(f"\n--- [{version}] Testing removed reserved word: {word} ---")
    
    error = None
    try:
        execute_query(conn, f"CREATE TABLE {word} (id INT);")
    except Exception as e:
        error = e

    if version == 'mysql80':
        if error:
            print(f"[{version}] Result: DDL with word '{word}' FAILED as expected.")
            assert True # Just check that it failed
        else:
            pytest.fail(f"[{version}] DDL with word '{word}' succeeded unexpectedly.")
    elif version == 'mysql84':
        if error:
            pytest.fail(f"[{version}] DDL with word '{word}' failed unexpectedly: {error}")
        else:
            print(f"[{version}] Result: DDL with word '{word}' SUCCEEDED as expected.")
            assert True
