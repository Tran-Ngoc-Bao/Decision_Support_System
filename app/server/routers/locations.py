from typing import List

from fastapi import Depends, HTTPException, Query, APIRouter
from psycopg2.extras import RealDictCursor

from ..dependency.db_connect import get_db_connection
from ..model.models import LocationItem

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/provinces", response_model=List[LocationItem])
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

@router.get("/districts", response_model=List[LocationItem])
def get_districts(province_id: int = Query(None), conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if province_id:
                cur.execute("SELECT id, name FROM public.districts WHERE province_id = %s", (province_id,))
            else:
                cur.execute("SELECT id, name FROM public.districts")
            districts = cur.fetchall()
        conn.close()
        return districts
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

@router.get("/wards", response_model=List[LocationItem])
def get_wards(district_id: int = Query(None), conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if district_id:
                cur.execute("SELECT id, name FROM public.wards WHERE district_id = %s", (district_id,))
            else:
                cur.execute("SELECT id, name FROM public.wards")
            wards = cur.fetchall()
        conn.close()
        return wards
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")