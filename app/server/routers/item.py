from typing import List

from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor

from ..dependency.db_connect import get_db_connection
from ..model.models import HouseTypeItem, EnvironmentItem

router = APIRouter(prefix="/item", tags=["locations"])

@router.get("/house-types", response_model=List[HouseTypeItem])
def get_house_types(conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT DISTINCT house_type as name FROM public.house_rent WHERE house_type IS NOT NULL ORDER BY name")
            house_types = cur.fetchall()
        conn.close()
        return house_types
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

@router.get("/amenities", response_model=List[EnvironmentItem])
def get_amenities(conn=Depends(get_db_connection)):
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, category, value FROM public.environment WHERE category IS NOT NULL ORDER BY category")
            amenities = cur.fetchall()
        conn.close()
        return amenities
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
