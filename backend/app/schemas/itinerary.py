from pydantic import BaseModel
from datetime import date, datetime
from typing import Literal


ItineraryStatus = str  # not_started / in_progress / completed


# ── 每日明细 ──────────────────────────────────────────────────────

class AttachmentOut(BaseModel):
    id: int
    file_key: str
    file_url: str
    original_name: str

    model_config = {"from_attributes": True}


class DayCreate(BaseModel):
    day_number: int
    date: date
    details: str = ""
    accommodation_area: str | None = None
    notes: str | None = None


class DayUpdate(BaseModel):
    details: str | None = None
    accommodation_area: str | None = None
    notes: str | None = None


class DayOut(BaseModel):
    id: int
    day_number: int
    date: date
    details: str
    accommodation_area: str | None
    notes: str | None
    attachments: list[AttachmentOut] = []

    model_config = {"from_attributes": True}


# ── 行程 ──────────────────────────────────────────────────────────

class ItineraryCreate(BaseModel):
    name: str
    origin: str
    destination: str
    days: int
    departure_date: date
    tags: list[str] | None = None
    notes: str | None = None
    customer_name: str
    customer_phone: str
    pax: int
    travelers: str | None = None
    order_id: int | None = None
    days_detail: list[DayCreate] = []


class ItineraryUpdate(BaseModel):
    name: str | None = None
    origin: str | None = None
    destination: str | None = None
    days: int | None = None
    departure_date: date | None = None
    tags: list[str] | None = None
    notes: str | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    pax: int | None = None
    travelers: str | None = None
    order_id: int | None = None
    status: str | None = None
    days_detail: list[DayCreate] | None = None


class ItineraryListItem(BaseModel):
    id: int
    name: str
    customer_name: str
    origin: str
    destination: str
    departure_date: date
    days: int
    status: str
    order_id: int | None
    share_token: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ItineraryOut(BaseModel):
    id: int
    name: str
    origin: str
    destination: str
    days: int
    departure_date: date
    tags: list[str] | None
    notes: str | None
    customer_name: str
    customer_phone: str
    pax: int
    travelers: str | None
    status: str
    order_id: int | None
    share_token: str | None
    created_at: datetime
    updated_at: datetime
    days_detail: list[DayOut] = []

    model_config = {"from_attributes": True}


class ItineraryStatusUpdate(BaseModel):
    status: str  # not_started / in_progress / completed


class ShareTokenResponse(BaseModel):
    share_token: str
    share_url: str
