from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal


OrderStatus = Literal["pending_deposit", "pending_payment", "completed"]


class OrderCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    customer_name: str
    customer_phone: Optional[str] = None
    travel_date: Optional[date] = None
    days: Optional[int] = None
    people_count: int = 1
    price: Optional[Decimal] = None
    deposit: Optional[Decimal] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    cost: Optional[Decimal] = None
    remarks: Optional[str] = None


class OrderUpdate(BaseModel):
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    travel_date: Optional[date] = None
    days: Optional[int] = None
    people_count: Optional[int] = None
    price: Optional[Decimal] = None
    deposit: Optional[Decimal] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    cost: Optional[Decimal] = None
    remarks: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderListItem(BaseModel):
    id: int
    order_no: str
    product_name: str
    customer_name: str
    customer_phone: Optional[str]
    travel_date: Optional[date]
    days: Optional[int]
    people_count: int
    price: Optional[Decimal]
    deposit: Optional[Decimal]
    supplier_name: Optional[str]
    cost: Optional[Decimal]
    profit: Optional[Decimal]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderOut(OrderListItem):
    product_id: Optional[int]
    supplier_id: Optional[int]
    remarks: Optional[str]
    updated_at: datetime


class OrderListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[OrderListItem]
