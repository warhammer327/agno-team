import psycopg2
from typing import List
from app.config import config


def scan_databases() -> List[str]:
    """List all non-template databases in the Postgres server."""
    conn = psycopg2.connect(
        dbname="postgres",  # must connect to a default DB
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
    )
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    databases = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return databases
