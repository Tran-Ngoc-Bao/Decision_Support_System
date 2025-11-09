from pydantic import BaseModel
from typing import List

class ItemSearch(BaseModel):
    province_id: int | None = None
    district_id: int | None = None
    ward_id: int | None = None
    search_content: str | None = None
    persons: int | None = None
    price_min: float | None = None
    price_max: float | None = None
    acreage_min: float | None = None
    acreage_max: float | None = None
    house_type: str | None = None
    contract_period: str | None = None
    bedrooms: int | None = None
    living_rooms: int | None = None
    kitchens: int | None = None

class HouseRentListRequest(BaseModel):
    house_rent_ids: List[int] = []