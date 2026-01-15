import time
import numpy as np
from typing import List, Dict, Any

class MetricsCollector:
    def __init__(self):
        self.latencies = [] # in milliseconds
        self.errors = 0
        self.start_time = 0
        self.end_time = 0
        self.total_requests = 0

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def add_latency(self, latency_ms: float):
        self.latencies.append(latency_ms)
        self.total_requests += 1

    def add_error(self):
        self.errors += 1
        self.total_requests += 1

    def calculate_report(self) -> Dict[str, Any]:
        duration = self.end_time - self.start_time
        count = len(self.latencies)
        
        if count == 0:
            return {
                "total_requests": self.total_requests,
                "success_count": 0,
                "error_count": self.errors,
                "duration_sec": duration,
                "qps": 0,
                "p50_latency": 0,
                "p95_latency": 0,
                "p99_latency": 0,
                "avg_latency": 0,
                "min_latency": 0,
                "max_latency": 0
            }

        lat_array = np.array(self.latencies)
        qps = self.total_requests / duration if duration > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "success_count": count,
            "error_count": self.errors,
            "duration_sec": duration,
            "qps": round(qps, 2),
            "p50_latency": round(np.percentile(lat_array, 50), 3),
            "p95_latency": round(np.percentile(lat_array, 95), 3),
            "p99_latency": round(np.percentile(lat_array, 99), 3),
            "avg_latency": round(np.mean(lat_array), 3),
            "min_latency": round(np.min(lat_array), 3),
            "max_latency": round(np.max(lat_array), 3)
        }
