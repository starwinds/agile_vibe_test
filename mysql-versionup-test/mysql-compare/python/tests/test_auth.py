import pytest
from common_db import get_db_connection
from config import AUTH_USERS

@pytest.mark.parametrize("user_key", ["native_user", "sha2_user"])
@pytest.mark.parametrize("driver", ["mysql.connector", "pymysql"])
def test_authentication_comparison(user_key, driver):
    """
    Compares authentication behavior between MySQL 8.0 and 8.4.
    The goal is to observe and report differences, not to pass/fail in a traditional sense.
    """
    user_info = AUTH_USERS[user_key]
    results = {}

    print(f"\n--- Comparing auth for user '{user_key}' with driver '{driver}' ---")

    # Test against MySQL 8.0
    conn80 = get_db_connection("mysql80", user=user_info["user"], password=user_info["password"], driver=driver)
    results["mysql80"] = "SUCCESS" if conn80 else "FAIL"
    if conn80:
        conn80.close()

    # Test against MySQL 8.4
    conn84 = get_db_connection("mysql84", user=user_info["user"], password=user_info["password"], driver=driver)
    results["mysql84"] = "SUCCESS" if conn84 else "FAIL"
    if conn84:
        conn84.close()

    print(f"Result for MySQL 8.0: {results['mysql80']}")
    print(f"Result for MySQL 8.4: {results['mysql84']}")

    # This assertion will fail if the behavior is different, highlighting the change.
    if results["mysql80"] != results["mysql84"]:
        pytest.fail(f"Authentication behavior differs for {user_key} with {driver}: 8.0 is {results['mysql80']}, 8.4 is {results['mysql84']}")
