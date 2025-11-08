from http.client import HTTPException
import os
from typing import List, Optional
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        port=os.environ.get("POSTGRES_PORT")
    )
    return conn

def get_list_ward_ids(
    province_id: Optional[int],
    district_id: Optional[int],
    ward_id: Optional[int],
    conn
) -> List[int]:
    try:
        if ward_id is not None:
            return [ward_id]

        sql = """
            SELECT w.id
            FROM public.wards w
            JOIN public.districts d ON w.district_id = d.id
            JOIN public.provinces p ON d.province_id = p.id
        """
        conditions = []
        params = []
        if province_id is not None:
            conditions.append("p.id = %s")
            params.append(province_id)
        if district_id is not None:
            conditions.append("d.id = %s")
            params.append(district_id)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            ward_ids = [row[0] for row in cur.fetchall()]

        return ward_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ward IDs: {e}")
    
def get_lists_environment_ids(
    search: Optional[str],
    conn
) -> List[int]:
    try:
        sql = "SELECT e.id FROM public.environment e"
        params = []

        if search is not None and str(search).strip() != "":
            sql += " WHERE e.value ILIKE %s"
            params.append(f"%{search}%")

        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            environment_ids = [row[0] for row in cur.fetchall()]

        return environment_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve environment IDs: {e}")