from pydantic import BaseModel
from rpds import List

class ItemSearch(BaseModel):
    province_id: int = None
    district_id: int = None
    ward_id: int = None
    search_content: str = None
    persons: int = None
    price_min: float = None
    price_max: float = None
    acreage_min: float = None
    acreage_max: float = None
    house_type: str = None
    contract_period: str = None
    bedrooms: int = None
    living_rooms: int = None
    kitchens: int = None

class HouseRentListRequest(BaseModel):
    house_rent_ids: List[int] = []