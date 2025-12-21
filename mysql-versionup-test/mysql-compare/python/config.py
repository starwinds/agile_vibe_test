# Database connection configurations
DB_CONFIGS = {
    "mysql80": {
        "host": "127.0.0.1",
        "port": 33060,
        "user": "root",
        "password": "test",
        "database": "testdb",
    },
    "mysql84": {
        "host": "127.0.0.1",
        "port": 33061,
        "user": "root",
        "password": "test",
        "database": "testdb",
    },
}

# Users for authentication tests
AUTH_USERS = {
    "native_user": {
        "user": "native_user",
        "password": "password"
    },
    "sha2_user": {
        "user": "sha2_user",
        "password": "password"
    }
}
