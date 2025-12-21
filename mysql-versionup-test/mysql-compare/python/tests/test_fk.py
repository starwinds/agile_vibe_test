import pytest
from common_db import execute_query

def test_fk_no_parent_pk(db_connection):
    """
    Tests Foreign Key creation when the referenced column is not a PK or UNIQUE.
    """
    conn, version = db_connection
    print(f"\n--- [{version}] Testing FK creation without parent PK/UNIQUE ---")
    
    error = None
    try:
        execute_query(conn, "CREATE TABLE parent (id INT) ENGINE=InnoDB;")
        execute_query(conn, "CREATE TABLE child (id INT, parent_id INT, FOREIGN KEY (parent_id) REFERENCES parent(id)) ENGINE=InnoDB;")
        
        # Check if FK was actually created
        res = execute_query(conn, 
            """
            SELECT COUNT(*) FROM information_schema.referential_constraints 
            WHERE constraint_schema = 'testdb' AND table_name = 'child';
            """, 
            fetch='one'
        )
        fk_created = res[0] > 0
        
    except Exception as e:
        error = e

    if error:
        print(f"[{version}] Result: FK creation FAILED as expected.")
        print(f"[{version}] Error Code: {error.errno}, Msg: {error.msg}")
        assert True # The operation failed, which is the expected behavior in strict modes
    elif fk_created:
        print(f"[{version}] Result: FK creation SUCCEEDED and constraint exists.")
        assert True
    else:
        print(f"[{version}] Result: DDL SUCCEEDED but constraint was NOT created (likely a warning).")
        pytest.fail(f"[{version}] DDL was accepted but no FK constraint was created.")


def test_fk_column_type_mismatch(db_connection):
    """
    Tests FK creation with mismatched column types (INT vs BIGINT).
    """
    conn, version = db_connection
    print(f"\n--- [{version}] Testing FK creation with column type mismatch ---")
    
    error = None
    try:
        execute_query(conn, "CREATE TABLE parent_type (id BIGINT PRIMARY KEY) ENGINE=InnoDB;")
        execute_query(conn, "CREATE TABLE child_type (id INT, parent_id INT, FOREIGN KEY (parent_id) REFERENCES parent_type(id)) ENGINE=InnoDB;")
    except Exception as e:
        error = e

    if error:
        print(f"[{version}] Result: FK creation with type mismatch FAILED.")
        print(f"[{version}] Error Code: {error.errno}, Msg: {error.msg}")
        assert True # Failure is an expected outcome
    else:
        print(f"[{version}] Result: FK creation with type mismatch SUCCEEDED.")
        pytest.fail(f"[{version}] FK with type mismatch was created unexpectedly.")

def test_fk_column_length_mismatch(db_connection):
    """
    Tests FK creation with mismatched column lengths (VARCHAR(191) vs VARCHAR(255)).
    This is generally allowed by MySQL.
    """
    conn, version = db_connection
    print(f"\n--- [{version}] Testing FK creation with column length mismatch ---")
    
    error = None
    try:
        execute_query(conn, "CREATE TABLE parent_len (id VARCHAR(255) PRIMARY KEY) ENGINE=InnoDB;")
        execute_query(conn, "CREATE TABLE child_len (id INT, parent_id VARCHAR(191), FOREIGN KEY (parent_id) REFERENCES parent_len(id)) ENGINE=InnoDB;")
    except Exception as e:
        error = e

    if error:
        pytest.fail(f"[{version}] FK with length mismatch failed unexpectedly: {error}")
    else:
        # This is the expected outcome. Verify the constraint was created.
        res = execute_query(conn, 
            """
            SELECT COUNT(*) FROM information_schema.referential_constraints 
            WHERE constraint_schema = 'testdb' AND table_name = 'child_len';
            """, 
            fetch='one'
        )
        if res[0] > 0:
            print(f"[{version}] Result: FK creation with length mismatch SUCCEEDED as expected.")
            assert True
        else:
            pytest.fail(f"[{version}] FK with length mismatch DDL passed but constraint not created.")

def test_fk_collation_mismatch(db_connection):
    """
    Tests FK creation with mismatched collations.
    This is generally not allowed by MySQL.
    """
    conn, version = db_connection
    print(f"\n--- [{version}] Testing FK creation with collation mismatch ---")
    
    error = None
    try:
        execute_query(conn, "CREATE TABLE parent_coll (id VARCHAR(50) PRIMARY KEY) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
        execute_query(conn, "CREATE TABLE child_coll (id INT, parent_id VARCHAR(50), FOREIGN KEY (parent_id) REFERENCES parent_coll(id)) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;")
    except Exception as e:
        error = e

    if error:
        print(f"[{version}] Result: FK creation with collation mismatch FAILED as expected.")
        print(f"[{version}] Error Code: {error.errno}, Msg: {error.msg}")
        assert True # Failure is the expected outcome
    else:
        pytest.fail(f"[{version}] FK with collation mismatch was created unexpectedly.")
