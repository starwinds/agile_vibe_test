import pytest
import time
from common_db import execute_query

# --- Test Configuration ---
NUM_ROWS_PERF = 50000
NUM_SELECTS = 10000
WARMUP_ROWS = 1000
BATCH_SIZE = 1000 # For executemany

@pytest.fixture(scope="class")
def perf_db(db_connection):
    """
    Fixture for the perf test class. Creates table and yields connection.
    """
    conn, version = db_connection
    table_name = "perf_test"
    
    # Setup Table
    execute_query(conn, f"""
        CREATE TABLE {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            uuid CHAR(36),
            data TEXT
        ) ENGINE=InnoDB;
    """)
    
    print(f"\n--- [{version}] Populating table with {NUM_ROWS_PERF} rows for perf tests ---")
    cursor = conn.cursor()
    for i in range(0, NUM_ROWS_PERF, BATCH_SIZE):
        batch_data = [(f'uuid_{j}', 'some data') for j in range(i, i + BATCH_SIZE)]
        cursor.executemany(f"INSERT INTO {table_name} (uuid, data) VALUES (%s, %s)", batch_data)
    conn.commit()
    cursor.close()
    print(f"[{version}] Population complete.")

    yield conn, version, table_name
    
    # Teardown is handled by the drop_all_tables in the db_connection fixture

@pytest.mark.usefixtures("perf_db")
class TestPerformance:
    
    def test_insert_tps(self, perf_db, record_property):
        """
        Measures the TPS for bulk inserts using executemany.
        """
        conn, version, table_name = perf_db
        print(f"\n--- [{version}] Testing Insert TPS (executemany) ---")

        insert_data = [(f'tps_uuid_{i}', 'tps data') for i in range(NUM_ROWS_PERF)]
        
        start_time = time.time()
        cursor = conn.cursor()
        for i in range(0, NUM_ROWS_PERF, BATCH_SIZE):
            batch = insert_data[i:i+BATCH_SIZE]
            cursor.executemany(f"INSERT INTO {table_name} (uuid, data) VALUES (%s, %s)", batch)
        conn.commit()
        cursor.close()
        end_time = time.time()

        duration = end_time - start_time
        tps = NUM_ROWS_PERF / duration

        record_property("tps", tps)
        print(f"[{version}] Result: Inserted {NUM_ROWS_PERF} rows in {duration:.2f} seconds.")
        print(f"[{version}] TPS: {tps:.2f}")
        assert tps > 0

    def test_select_latency(self, perf_db, record_property):
        """
        Measures the average latency for PK-based lookups.
        """
        conn, version, table_name = perf_db
        print(f"\n--- [{version}] Testing Select Latency ---")
        
        # Warm-up
        print(f"[{version}] Performing warm-up selects: {WARMUP_ROWS} queries")
        for i in range(1, WARMUP_ROWS + 1):
            execute_query(conn, f"SELECT data FROM {table_name} WHERE id = {i};", fetch='one')

        # Main test
        print(f"[{version}] Selecting {NUM_SELECTS} rows by PK...")
        start_time = time.time()
        for i in range(1, NUM_SELECTS + 1):
            execute_query(conn, f"SELECT data FROM {table_name} WHERE id = {i};", fetch='one')
        end_time = time.time()

        duration = end_time - start_time
        avg_latency_ms = (duration / NUM_SELECTS) * 1000

        record_property("avg_latency_ms", avg_latency_ms)
        print(f"[{version}] Result: Performed {NUM_SELECTS} lookups in {duration:.2f} seconds.")
        print(f"[{version}] Average Latency: {avg_latency_ms:.4f} ms")
        assert avg_latency_ms > 0