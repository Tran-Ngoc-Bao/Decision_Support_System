from typing import List

from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from collections import defaultdict

from ..dependency.db_connect import get_db_connection
from ..model.models import CompareRequest, CompareResultItem

router = APIRouter(prefix="/dss", tags=["DSS"])

@router.post("/compare", response_model=List[CompareResultItem])
def compare(request: CompareRequest, conn=Depends(get_db_connection)):
    if not request.house_rent_ids:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT hr.*, w.name as ward_name, d.name as district_name, p.name as province_name
                FROM house_rent hr
                LEFT JOIN wards w ON hr.ward_id = w.id
                LEFT JOIN districts d ON w.district_id = d.id
                LEFT JOIN provinces p ON d.province_id = p.id
                WHERE hr.id = ANY(%s)
                """,
                (request.house_rent_ids,)
            )
            house_data = cur.fetchall()

        ranked_results = _data_vectorizer(house_data, )

        conn.close()
        return ranked_results
    except Exception as e:
        print(f"ERROR in run_topsis_analysis: {e}")
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")


def _data_vectorizer(house_data: list):
    pass