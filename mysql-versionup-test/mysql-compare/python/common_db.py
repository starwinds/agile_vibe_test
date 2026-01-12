import mysql.connector
import pymysql
from config import DB_CONFIGS

def get_db_connection(version, user=None, password=None, driver='mysql.connector'):
    """Establishes a database connection. 'version' can be a key in DB_CONFIGS or a dict."""
    if isinstance(version, dict):
        config = version.copy()
    else:
        config = DB_CONFIGS.get(version)
        if not config:
            raise ValueError(f"Invalid MySQL version specified: {version}")

    # Override user and password if provided
    conn_config = config.copy()
    if user:
        conn_config['user'] = user
    if password:
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
        # print(f"Failed to connect: {e}") # Reduce noise
        return None

def get_cluster_primary(nodes_list):
    """
    Identifies the Primary node in an InnoDB Cluster from a list of connection configs.
    Returns the config dict of the Primary node.
    """
    for node_config in nodes_list:
        conn = get_db_connection(node_config)
        if not conn:
            continue
        
        try:
            cursor = conn.cursor()
            # Check if this node thinks it is Primary
            # reliable way: check replication_group_members where member_id is local
            cursor.execute("SELECT MEMBER_ROLE FROM performance_schema.replication_group_members WHERE MEMBER_ID = @@server_uuid")
            row = cursor.fetchone()
            if row and row[0] == 'PRIMARY':
                conn.close()
                return node_config
        except Exception as e:
            print(f"Error checking node {node_config.get('port')}: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()
    
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
