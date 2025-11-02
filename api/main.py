from fastapi import FastAPI, Depends
from typing import List
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        port=os.environ.get("POSTGRES_PORT")
    )
    return conn

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI service!"}

@app.get("/db-check")
def db_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "success", "message": "Database connection successful!"}
    except Exception as e:
        return {"status": "error", "message": f"Database connection failed: {e}"}

@app.get("/provinces")
def get_provinces(conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM public.provinces")
            provinces = cur.fetchall()
        conn.close()
        return provinces
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
