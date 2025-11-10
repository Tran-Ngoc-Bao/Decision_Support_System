from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date, datetime

class DbCheck(BaseModel):
    """
    Response model for the database health check.
    """
    status: str
    message: str

class LocationItem(BaseModel):
    """
    Generic response model for a location item (province, district, ward).
    """
    id: int
    name: str

class EnvironmentTag(BaseModel):
    """
    Response model for an environment tag.
    """
    id: int
    category: str
    value: str

class HouseTypeItem(BaseModel):
    """
    Response model for a house type.
    """
    name: str

class EnvironmentItem(BaseModel):
    """
    Response model for an environment item.
    """
    id: int
    category: str
    value: str

class HouseRentItem(BaseModel):
    """
    Response model for a single house rent listing.
    """
    id: int
    available: bool
    published: date
    price: float
    acreage: float
    address: str
    house_number: Optional[str] = None
    street: Optional[str] = None
    ward_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    title: str
    phone_number: Optional[str] = None
    create_time: datetime
    update_time: datetime
    house_type: Optional[str] = None
    contract_period: Optional[str] = None
    bedrooms: Optional[int] = None
    living_rooms: Optional[int] = None
    kitchens: Optional[int] = None
    ward_name: str
    district_name: str
    province_name: str
    environments: List[EnvironmentTag] = []

class CompareRequest(BaseModel):
    """
    Request model for the TOPSIS endpoint.
    """
    house_rent_ids: List[int]
    amenities: Optional[List[int]]
    weights: Optional[List[int]]
    topsis_weight: Optional[List[float]]

class CompareResultItem(HouseRentItem):
    """
    Response model for a single item in the TOPSIS result list.
    """
    topsis_score: float
    rank: int

class TopsisCompareResponse(BaseModel):
    """
    Response model for the full TOPSIS comparison result.
    """
    ranked_houses: List[CompareResultItem]
    ideal_best: Dict[str, float]
    ideal_worst: Dict[str, float]
