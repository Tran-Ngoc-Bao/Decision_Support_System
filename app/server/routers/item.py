from typing import List

from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor

from ..dependency.db_connect import get_db_connection
from ..model.models import HouseTypeItem

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

