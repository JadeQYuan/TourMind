from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Literal


ItineraryStatus = str  # not_started / in_progress / completed
OrderStatus = str  # pending / confirmed / cancelled
ServiceType = Literal[
    "transport", "accommodation", "attraction", "meal", "guide", "insurance", "other"
]


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


# ── 订单 ──────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    supplier_id: int | None = None
    service_type: ServiceType
    amount: Decimal
    order_date: date
    related_days: list[int] | None = None
    notes: str | None = None


class OrderUpdate(BaseModel):
    supplier_id: int | None = None
    service_type: ServiceType | None = None
    amount: Decimal | None = None
    order_date: date | None = None
    related_days: list[int] | None = None
    notes: str | None = None
    status: OrderStatus | None = None


class OrderAttachmentOut(BaseModel):
    id: int
    file_key: str
    file_url: str
    original_name: str

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    supplier_id: int | None
    service_type: str
    amount: Decimal
    order_date: date
    related_days: list[int] | None
    status: str
    notes: str | None
    attachments: list[OrderAttachmentOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderListOut(BaseModel):
    """跨行程订单汇总视图"""
    id: int
    itinerary_id: int
    itinerary_name: str
    supplier_id: int | None
    supplier_name: str | None
    service_type: str
    amount: Decimal
    order_date: date
    status: str
    notes: str | None
    created_at: datetime


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
    customer_order_id: int | None = None
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
    customer_order_id: int | None = None
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
    customer_order_id: int | None
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
    customer_order_id: int | None
    share_token: str | None
    created_at: datetime
    updated_at: datetime
    days_detail: list[DayOut] = []
    orders: list[OrderOut] = []

    model_config = {"from_attributes": True}


class ItineraryStatusUpdate(BaseModel):
    status: str  # not_started / in_progress / completed


class ShareTokenResponse(BaseModel):
    share_token: str
    share_url: str
