from typing import List

from fastapi import Query, Depends, HTTPException, APIRouter

from ..dependency.db_connect import get_db_connection
from ..logic.house import HouseService
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
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        conn=Depends(get_db_connection)
):
    """
    Search for house rent listings with various filters
    """
    try:
        results = HouseService.search_house_rent(
            conn=conn,
            province_id=province_id,
            district_id=district_id,
            ward_id=ward_id,
            min_price=min_price,
            max_price=max_price,
            min_acreage=min_acreage,
            max_acreage=max_acreage,
            house_type=house_type,
            contract_period=contract_period,
            bedrooms=bedrooms,
            living_rooms=living_rooms,
            kitchens=kitchens,
            limit=limit,
            offset=offset
        )

        return results

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in search_house_rent: {e}")
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")