from pydantic import BaseModel
from datetime import datetime
from typing import Optional


ProductStatus = str  # "active" | "inactive"


class ItineraryTemplateDay(BaseModel):
    seq: int
    details: str
    accommodation_area: Optional[str] = None
    notes: Optional[str] = None


class ProductCreate(BaseModel):
    name: str
    product_type: Optional[str] = None
    origin: Optional[str] = None
    destination: str
    days: int
    reference_price: Optional[float] = None
    includes: Optional[str] = None
    excludes: Optional[str] = None
    cancellation_policy: Optional[str] = None
    travel_notice: Optional[str] = None
    important_tips: Optional[str] = None
    itinerary_template: Optional[list[ItineraryTemplateDay]] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None
    status: str = "active"


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    product_type: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    days: Optional[int] = None
    reference_price: Optional[float] = None
    includes: Optional[str] = None
    excludes: Optional[str] = None
    cancellation_policy: Optional[str] = None
    travel_notice: Optional[str] = None
    important_tips: Optional[str] = None
    itinerary_template: Optional[list[ItineraryTemplateDay]] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    product_type: Optional[str]
    origin: Optional[str]
    destination: str
    days: int
    reference_price: Optional[float]
    includes: Optional[str]
    excludes: Optional[str]
    cancellation_policy: Optional[str]
    travel_notice: Optional[str]
    important_tips: Optional[str]
    itinerary_template: Optional[list[dict]]
    tags: Optional[list[str]]
    notes: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListItem(BaseModel):
    id: int
    name: str
    product_type: Optional[str]
    destination: str
    days: int
    reference_price: Optional[float]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
