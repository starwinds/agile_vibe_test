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

# Cluster Node Configurations
CLUSTER_CONFIGS = {
    "mysql80": [
        {"host": "127.0.0.1", "port": 33062, "user": "root", "password": "rootpassword", "database": "mysql"},
        {"host": "127.0.0.1", "port": 33063, "user": "root", "password": "rootpassword", "database": "mysql"},
        {"host": "127.0.0.1", "port": 33064, "user": "root", "password": "rootpassword", "database": "mysql"},
    ],
    "mysql84": [
        {"host": "127.0.0.1", "port": 33065, "user": "root", "password": "rootpassword", "database": "mysql"},
        {"host": "127.0.0.1", "port": 33066, "user": "root", "password": "rootpassword", "database": "mysql"},
        {"host": "127.0.0.1", "port": 33067, "user": "root", "password": "rootpassword", "database": "mysql"},
    ]
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
