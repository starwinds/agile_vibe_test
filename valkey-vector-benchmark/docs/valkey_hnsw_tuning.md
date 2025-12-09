# Valkey HNSW Tuning Guide

This guide explains how to tune HNSW parameters for Valkey Vector Search to achieve the best balance between performance (QPS/Latency) and accuracy (Recall).

## Key Parameters

### 1. `M` (Max Connections)
- **Description**: The maximum number of outgoing connections for each node in the graph.
- **Impact**:
  - **Higher M**: Better recall, but higher memory usage and slower indexing/search.
  - **Lower M**: Lower memory usage and faster indexing, but potentially lower recall.
- **Recommended Range**: 16 - 64. Start with 16.

### 2. `EF_CONSTRUCTION`
- **Description**: The size of the dynamic candidate list during index construction.
- **Impact**:
  - **Higher Value**: Better index quality (higher recall potential), but significantly slower indexing time.
  - **Lower Value**: Faster indexing, but lower index quality.
- **Recommended Range**: 100 - 500. Start with 200.

### 3. `EF_RUNTIME`
- **Description**: The size of the dynamic candidate list during search.
- **Impact**:
  - **Higher Value**: Higher recall, but higher latency (lower QPS).
  - **Lower Value**: Lower latency (higher QPS), but lower recall.
- **Recommended Range**: 10 - 200. Adjust this dynamically based on your recall requirements.

## Tuning Strategy

1. **Fix `M` and `EF_CONSTRUCTION`**: Set `M=16` and `EF_CONSTRUCTION=200` as a baseline.
2. **Tune `EF_RUNTIME`**: Run benchmarks with varying `EF_RUNTIME` (e.g., 10, 20, 40, 80, 100, 200).
3. **Analyze Trade-off**: Plot Recall vs. QPS. Choose the `EF_RUNTIME` that meets your recall target (e.g., 0.95) with the highest QPS.
4. **Iterate**: If recall is insufficient even at high `EF_RUNTIME`, increase `M` or `EF_CONSTRUCTION` and repeat.

## Example Configuration

```yaml
db_case_config:
  index_name: vdbbench_idx
  prefix: doc:
  M: 32
  EF_CONSTRUCTION: 400
  EF_RUNTIME: 100
  distance_metric: COSINE
```
