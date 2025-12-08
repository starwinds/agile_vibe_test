# Valkey Client for VectorDBBench

This directory contains the Valkey backend client for VectorDBBench, allowing you to benchmark Valkey's vector search capabilities.

## Prerequisites

- Python 3.11+
- Valkey Server (with Vector Search module enabled, e.g., Valkey 8.0+ or compatible)
- `valkey` Python client

## Installation

1. Install VectorDBBench dependencies:
   ```bash
   pip install -e .
   ```
2. Install `valkey` client:
   ```bash
   pip install valkey
   ```

## Configuration

The Valkey client uses `ValkeyDBConfig` for connection settings and `ValkeyDBCaseConfig` for index parameters.

### `valkey_bench_config.yaml` Example

```yaml
db: Valkey
db_config:
  host: 127.0.0.1
  port: 6379
  password: null

cases:
  - case_id: 1
    label: valkey-hnsw
    dataset:
      name: glove-100-angular
      size: 10000
      dim: 100
    db_case_config:
      index_name: vdbbench_idx
      prefix: doc:
      M: 16
      EF_CONSTRUCTION: 200
      EF_RUNTIME: 10
      distance_metric: COSINE
```

## Usage

### CLI

Run the benchmark using the configuration file:

```bash
vectordbbench test --config-file valkey_bench_config.yaml
```

### Python API

```python
from vectordb_bench.backend.clients.valkey.config import ValkeyDBConfig, ValkeyDBCaseConfig
from vectordb_bench.backend.clients.valkey.new_client import ValkeyClient
from vectordb_bench.backend.clients import MetricType

# Configuration
db_config = ValkeyDBConfig(host="localhost", port=6379)
case_config = ValkeyDBCaseConfig(
    index_name="test_idx",
    prefix="doc:",
    M=16,
    EF_CONSTRUCTION=200,
    EF_RUNTIME=10,
    distance_metric=MetricType.COSINE
)

# Initialize Client
client = ValkeyClient(dim=128, db_config=db_config, db_case_config=case_config, drop_old=True)

# Load Data
embeddings = [[0.1] * 128]
metadata = [1]
with client.init():
    client.insert_embeddings(embeddings, metadata)

# Search
query = [0.1] * 128
with client.init():
    results = client.search_embedding(query, k=1)
    print(results)
```

## Testing

Run unit tests:

```bash
pytest tests/test_valkey_client.py
```
