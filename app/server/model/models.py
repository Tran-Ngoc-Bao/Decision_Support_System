from pydantic import BaseModel
from typing import Optional, List
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
    category: str
    value: str

class HouseTypeItem(BaseModel):
    """
    Response model for a house type.
    """
    name: str

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