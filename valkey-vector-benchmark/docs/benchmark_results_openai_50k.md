# Valkey Vector Search Benchmark Results

## Overview
- **Date**: 2025-12-15
- **Database**: Valkey Standalone
- **Dataset**: OpenAI Small (50,000 vectors, 1536 dimensions)
- **Case Type**: Performance1536D50K
- **Index Type**: HNSW (M=16, EF_Construction=200, EF_Runtime=10)

## Summary Metrics
- **Max QPS**: 4,073.42
- **Recall**: 0.1
- **Serial Latency (P99)**: 3.5 ms
- **Serial Latency (P95)**: 2.8 ms

## Concurrency Performance

| Concurrency | QPS | Avg Latency (ms) | P99 Latency (ms) |
| :--- | :--- | :--- | :--- |
| 1 | 497.73 | 2.01 | 3.29 |
| 5 | 2,272.91 | 2.20 | 3.82 |
| 10 | 3,167.68 | 3.15 | 5.22 |
| 20 | 3,527.53 | 5.65 | 11.26 |
| 30 | 3,608.01 | 8.29 | 15.47 |
| 40 | 4,073.42 | 9.78 | 16.38 |
| 60 | 3,872.75 | 15.41 | 26.49 |
| 80 | 3,496.20 | 20.73 | 38.83 |

## Observations
- **Peak Performance**: The system reached its peak throughput of **4,073 QPS** at a concurrency level of **40**.
- **Scalability**: Performance scaled well up to 40 concurrent clients. Beyond that (60, 80 clients), QPS slightly decreased, likely due to resource contention or context switching overhead.
- **Latency**: Latency remained very low (< 10ms average) even at peak throughput.

## Configuration Details
- **Host**: 127.0.0.1:6379
- **Metric Type**: COSINE
- **Search Parameters**: k=100
