from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum


class ItineraryStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class ItineraryAttachment(BaseModel):
    file_key: str
    file_url: str
    original_name: str
    created_at: Optional[datetime] = None


class ItineraryDayDetail(BaseModel):
    day_number: int
    date: date
    details: str
    accommodation_area: Optional[str] = None
    notes: Optional[str] = None
    attachments: List[ItineraryAttachment] = Field(default_factory=list)


class ItineraryBase(BaseModel):
    origin: str = Field(..., min_length=1, max_length=100)
    destination: str = Field(..., min_length=1, max_length=200)
    days: int = Field(..., ge=1)
    departure_date: date
    notes: Optional[str] = None
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: str = Field(..., min_length=1, max_length=20)
    pax: int = Field(..., ge=1)
    travelers: Optional[str] = None
    product_id: Optional[int] = None
    order_id: Optional[int] = None
    details: Optional[List[ItineraryDayDetail]] = None


class ItineraryCreate(ItineraryBase):
    pass


class ItineraryUpdate(BaseModel):
    origin: Optional[str] = Field(None, min_length=1, max_length=100)
    destination: Optional[str] = Field(None, min_length=1, max_length=200)
    days: Optional[int] = Field(None, ge=1)
    departure_date: Optional[date] = None
    notes: Optional[str] = None
    customer_name: Optional[str] = Field(None, min_length=1, max_length=100)
    customer_phone: Optional[str] = Field(None, min_length=1, max_length=20)
    pax: Optional[int] = Field(None, ge=1)
    travelers: Optional[str] = None
    status: Optional[ItineraryStatus] = None
    product_id: Optional[int] = None
    order_id: Optional[int] = None
    details: Optional[List[ItineraryDayDetail]] = None


class Itinerary(ItineraryBase):
    id: int
    status: str
    share_token: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ItineraryListItem(BaseModel):
    id: int
    origin: str
    destination: str
    days: int
    departure_date: date
    status: str
    customer_name: str
    product_id: Optional[int] = None
    order_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
