from typing import List

from fastapi import Query, Depends, HTTPException, APIRouter
from psycopg2.extras import RealDictCursor

from ..dependency.db_connect import get_db_connection
from ..model.models import HouseRentItem

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/house-rent", response_model=List[HouseRentItem])
def search_house_rent(
    province_id: int = Query(None),
    district_id: int = Query(None),
    ward_id: int = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    min_acreage: float = Query(None),
    max_acreage: float = Query(None),
    house_type: str = Query(None),
    contract_period: str = Query(None),
    bedrooms: int = Query(None),
    living_rooms: int = Query(None),
    kitchens: int = Query(None),
    limit: int = Query(10, ge=1, le=100), # Default limit to 10, min 1, max 100
    offset: int = Query(0, ge=0),       # Default offset to 0, min 0
    conn=Depends(get_db_connection)
):
    try:
        query = """
            SELECT hr.*, w.name as ward_name, d.name as district_name, p.name as province_name
            FROM house_rent hr
            LEFT JOIN wards w ON hr.ward_id = w.id
            LEFT JOIN districts d ON w.district_id = d.id
            LEFT JOIN provinces p ON d.province_id = p.id
            WHERE hr.available = TRUE
        """
        params = []
        
        def add_condition(field, value, operator="="):
            nonlocal query
            if value is not None:
                query += f" AND {field} {operator} %s"
                params.append(value)

        add_condition("p.id", province_id)
        add_condition("d.id", district_id)
        add_condition("hr.ward_id", ward_id)
        add_condition("hr.price", min_price, ">=")
        add_condition("hr.price", max_price, "<=")
        add_condition("hr.acreage", min_acreage, ">=")
        add_condition("hr.acreage", max_acreage, "<=")
        add_condition("hr.house_type", house_type)
        add_condition("hr.contract_period", contract_period)
        add_condition("hr.bedrooms", bedrooms)
        add_condition("hr.living_rooms", living_rooms)
        add_condition("hr.kitchens", kitchens)

        # Add LIMIT and OFFSET for pagination
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, tuple(params))
            results = cur.fetchall()
        conn.close()
        return results
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
