import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    if os.getenv('DOCKER_ENV') or os.path.exists('/.dockerenv'):
        # Đang chạy trong Docker - dùng hostname "database"
        db_host = 'database'
    else:
        # Đang chạy local - dùng localhost với port 5433
        db_host = 'localhost'

    conn = psycopg2.connect(
        host=db_host,
        port=os.getenv('POSTGRES_PORT', '5433'),  # 5433 cho local, 5432 trong Docker
        database=os.getenv('POSTGRES_DB', 'system'),
        user=os.getenv('POSTGRES_USER', 'admin'),
        password=os.getenv('POSTGRES_PASSWORD', 'admin')
    )
    return conn