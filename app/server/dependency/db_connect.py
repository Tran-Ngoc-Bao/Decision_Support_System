import psycopg2
import os

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        port=os.environ.get("POSTGRES_PORT")
    )
    return conn