import pytest
from common_db import get_db_connection, drop_all_tables

@pytest.fixture(scope="class", params=["mysql80", "mysql84"])
def db_connection(request):
    """Pytest fixture to provide a database connection for each version."""
    version = request.param
    conn = get_db_connection(version)
    
    if conn is None:
        pytest.fail(f"Could not connect to {version}")

    # Clean up database before test
    drop_all_tables(conn)

    yield conn, version

    # Teardown: clean up database after test
    # drop_all_tables(conn) # Disabling cleanup to inspect post-test state if needed
    conn.close()
