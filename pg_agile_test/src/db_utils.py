import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector, Vector

DB_NAME = "vector_demo"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"

def ensure_database_exists():
    """Ensures the specified database exists, creating it if necessary."""
    try:
        # Connect to the default 'postgres' database to check for our target database
        conn = psycopg.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            autocommit=True  # Use autocommit mode for database creation
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE {DB_NAME}")
        conn.close()
    except psycopg.OperationalError as e:
        # This can happen if the postgres database itself is not available
        print(f"Error ensuring database exists: {e}")
        raise

def connect():
    """Establishes a connection to the database, ensuring it exists first."""
    ensure_database_exists()  # Ensure the database is ready
    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        row_factory=dict_row
    )
    return conn

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        register_vector(conn)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS docs (
                id SERIAL PRIMARY KEY,
                item_name TEXT,
                category TEXT,
                content TEXT,
                embedding VECTOR(384)
            );
        """)
    conn.commit()

def insert_item(conn, item_name, category, content, vec):
    register_vector(conn)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO docs (item_name, category, content, embedding)
            VALUES (%s, %s, %s, %s)
        """, (item_name, category, content, Vector(vec)))
    conn.commit()

def search_similar(conn, query_vec, limit=3):
    register_vector(conn)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, item_name, category, content,
                   1 - (embedding <#> %s) AS similarity
            FROM docs
            ORDER BY embedding <#> %s ASC
            LIMIT %s
        """, (Vector(query_vec), Vector(query_vec), limit))
        return cur.fetchall()

def search_similar_euclidean(conn, query_vec, limit=3):
    register_vector(conn)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, item_name, category, content,
                   embedding <-> %s AS distance
            FROM docs
            ORDER BY embedding <-> %s ASC
            LIMIT %s
        """, (Vector(query_vec), Vector(query_vec), limit))
        return cur.fetchall()

def search_combined(conn, query_vec, category=None, limit=5, similarity_threshold=0.5):
    register_vector(conn)
    with conn.cursor() as cur:
        sql = "SELECT id, item_name, category, content, 1 - (embedding <=> %(qv)s) AS similarity FROM docs"
        
        params = {
            "qv": Vector(query_vec),
            "limit": limit,
            "similarity_threshold": similarity_threshold
        }
        
        where_clauses = []
        
        # Always filter by similarity
        where_clauses.append("(1 - (embedding <=> %(qv)s)) > %(similarity_threshold)s")
        
        # Optionally filter by category
        if category:
            where_clauses.append("category = %(category)s")
            params["category"] = category
            
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
            
        sql += " ORDER BY similarity DESC LIMIT %(limit)s"
        
        cur.execute(sql, params)
        results = cur.fetchall()
        return results