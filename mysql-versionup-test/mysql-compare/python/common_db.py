import mysql.connector
import pymysql
from config import DB_CONFIGS

def get_db_connection(version, user='root', password='test', driver='mysql.connector'):
    """Establishes a database connection."""
    config = DB_CONFIGS.get(version)
    if not config:
        raise ValueError(f"Invalid MySQL version specified: {version}")

    # Override user and password if provided
    conn_config = config.copy()
    conn_config['user'] = user
    conn_config['password'] = password

    try:
        if driver == 'mysql.connector':
            conn = mysql.connector.connect(**conn_config, connect_timeout=5)
        elif driver == 'pymysql':
            conn = pymysql.connect(**conn_config, connect_timeout=5)
        else:
            raise ValueError(f"Unsupported driver: {driver}")
        
        return conn
    except Exception as e:
        print(f"Failed to connect to {version} using {driver} with user {user}: {e}")
        return None

def execute_query(connection, query, fetch=None):
    """Executes a query and returns the result."""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        if fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'all':
            result = cursor.fetchall()
        else:
            connection.commit()
            result = None
        return result
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()

def drop_all_tables(connection):
    """Drops all tables in the current database."""
    try:
        cursor = connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        for (table_name,) in tables:
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()
    except Exception as e:
        print(f"Error dropping tables: {e}")
    finally:
        cursor.close()
