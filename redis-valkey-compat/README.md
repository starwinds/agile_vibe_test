# Redis 7.2.6 vs. Valkey 9.0 Compatibility Test Suite

## 1. Project Purpose

This project provides an automated test suite to compare the behavior of Redis 7.2.6 and Valkey 9.0. It runs a series of common command scenarios against both database instances and highlights any differences in their responses or behavior. The goal is to quickly assess the drop-in compatibility of Valkey for applications currently using Redis.

## 2. Required Tools

- **Docker & Docker Compose**: To run the Redis and Valkey database instances.
- **Python 3.10+**: To run the test runner application.
- **pip**: For installing Python package dependencies.

## 3. Execution Steps

Follow these steps to run the compatibility tests:

### Step 1: Start the Database Containers

From the `redis-valkey-compat` root directory, start the Redis and Valkey services in detached mode.

```bash
docker-compose up -d
```

This will start:
- `redis726` on `localhost:6379`
- `valkey900` on `localhost:6380`

You can verify they are running with `docker-compose ps`.

### Step 2: Set Up the Python Environment

Navigate into the test application directory and create a virtual environment.

```bash
cd app
python -m venv .venv
```

Activate the virtual environment:
- **On macOS and Linux:**
  ```bash
source .venv/bin/activate
  ```
- **On Windows:**
  ```bash
.venv\\Scripts\\activate
  ```

### Step 3: Install Dependencies

Install the required Python packages using pip.

```bash
pip install -r requirements.txt
```

### Step 4: Run the Test Suite

Execute the test runner script. The script will connect to both databases, run all scenarios, and print a summary table of the results.

```bash
python test_runner.py
```

## 4. Interpreting the Results

The script will output:
1.  **A summary table**: Shows the status (`OK`, `WARN`, `FAIL`, `ERROR`) of each test scenario for both Redis and Valkey.
2.  **A difference table**: If any behavioral differences are found, this table will explicitly detail the discrepancies between the two databases.
3.  **JSON output files**: `results_redis726.json` and `results_valkey900.json` are generated in the `app/` directory. These files contain the raw, detailed results from each test run for deeper analysis.

If the final message is "✅ No functional differences detected between targets," it means all tested scenarios behaved identically.

## 5. How to Extend Test Scenarios

You can easily add your own test cases to verify specific functionality.

1.  Create a new Python file in the `app/scenarios/` directory (e.g., `my_streams_test.py`).
2.  Inside the new file, define a function with the exact signature `run(client) -> dict`.
3.  Implement your test logic within this function. The function must return a dictionary with the keys `scenario_name`, `status`, and `detail`.
4.  The `test_runner.py` will automatically discover and execute your new scenario the next time it is run.

**Example `run` function:**
```python
# app/scenarios/my_streams_test.py

def run(client) -> dict:
    scenario_name = "my_streams_test"
    try:
        # Your test logic here...
        # ...
        return {
            "scenario_name": scenario_name,
            "status": "OK",
            "detail": "Streams test passed."
        }
    except Exception as e:
        return {
            "scenario_name": scenario_name,
            "status": "ERROR",
            "detail": f"An exception occurred: {str(e)}"
        }
```

## 6. Test Scenarios

The following scenarios are executed by the test suite:

-   **`basic_crud.py`**: Tests fundamental key-value operations like `SET`, `GET`, `EXISTS`, and `DELETE` to ensure they work as expected.
-   **`data_structures.py`**: Verifies the behavior of common data structures, including Lists (`LPUSH`, `LPOP`), Hashes (`HSET`, `HGET`), and Sets (`SADD`, `SISMEMBER`).
-   **`scan_and_iter.py`**: Checks the functionality of cursors for iterating over the keyspace using `SCAN`.
-   **`lua_and_tx.py`**: Ensures that Lua scripting (`EVAL`) and transaction blocks (`MULTI`/`EXEC`) are handled correctly.
-   **`pubsub.py`**: Validates the Publish/Subscribe mechanism by subscribing to a channel, publishing a message, and confirming its reception.
-   **`memory_eviction.py`**: Simulates a memory pressure scenario. It sets a `maxmemory` limit, fills the database to trigger key eviction, and verifies that the eviction policy (`allkeys-lru`) works.
-   **`large_payloads.py`**: Measures performance and compatibility when handling large data payloads (1MB, 5MB, 10MB), checking the latency of `SET`/`GET` and memory usage.
