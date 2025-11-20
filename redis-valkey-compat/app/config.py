# app/config.py

"""
Central configuration for the test runner.

This file defines the target endpoints for Redis and Valkey.
The structure is designed to be easily extensible for additional
parameters like passwords, database indexes, or SSL options.
"""

TARGETS = {
    "redis726": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        # "password": "your_password_if_any",
    },
    "valkey900": {
        "host": "localhost",
        "port": 6380,
        "db": 0,
        # "password": "your_password_if_any",
    },
}
