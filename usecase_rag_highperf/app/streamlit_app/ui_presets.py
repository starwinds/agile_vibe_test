from typing import List, Dict

PRESETS: List[Dict[str, str]] = [
    {
        "label": "Semantic 1",
        "query": "How to configure Valkey replication?",
        "mode": "semantic"
    },
    {
        "label": "Semantic 2",
        "query": "What is the policy for document retention?",
        "mode": "semantic"
    },
    {
        "label": "Semantic 3",
        "query": "Troubleshooting connection timeout issues",
        "mode": "semantic"
    },
    {
        "label": "Keyword 1",
        "query": "ERROR_503",
        "mode": "keyword"
    },
    {
        "label": "Keyword 2",
        "query": "max_connections",
        "mode": "keyword"
    },
    {
        "label": "Keyword 3",
        "query": "User Alice",
        "mode": "keyword"
    },
    {
        "label": "Hybrid 1",
        "query": "Configuration for MAX_MEMORY limit",
        "mode": "hybrid"
    },
    {
        "label": "Hybrid 2",
        "query": "Security patch CVE-2024-1234",
        "mode": "hybrid"
    },
    {
        "label": "Hybrid 3",
        "query": "Performance tuning for large datasets",
        "mode": "hybrid"
    }
]
