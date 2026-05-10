from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ItineraryTemplateDay(BaseModel):
    seq: int
    details: str
    accommodation_area: Optional[str] = None
    notes: Optional[str] = None


class ProductCreate(BaseModel):
    name: str
    origin: Optional[str] = None
    destination: str
    days: int
    price: float
    includes: Optional[str] = None
    excludes: Optional[str] = None
    cancellation_policy: Optional[str] = None
    travel_notice: Optional[str] = None
    important_tips: Optional[str] = None
    itinerary_template: Optional[list[ItineraryTemplateDay]] = None
    remark: Optional[str] = None
    status: str = "enabled"


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    days: Optional[int] = None
    price: Optional[float] = None
    includes: Optional[str] = None
    excludes: Optional[str] = None
    cancellation_policy: Optional[str] = None
    travel_notice: Optional[str] = None
    important_tips: Optional[str] = None
    itinerary_template: Optional[list[ItineraryTemplateDay]] = None
    remark: Optional[str] = None
    status: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    origin: Optional[str]
    destination: str
    days: int
    price: float
    includes: Optional[str]
    excludes: Optional[str]
    cancellation_policy: Optional[str]
    travel_notice: Optional[str]
    important_tips: Optional[str]
    itinerary_template: Optional[list[dict]]
    remark: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListItem(BaseModel):
    id: int
    name: str
    destination: str
    days: int
    price: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
