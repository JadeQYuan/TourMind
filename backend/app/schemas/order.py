from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal


OrderStatus = Literal["pending_deposit", "pending_payment", "completed"]


class OrderCreate(BaseModel):
    product_id: Optional[int] = None
    customer_name: str
    customer_phone: Optional[str] = None
    travel_date: Optional[date] = None
    days: Optional[int] = None
    people_count: int = 1
    price: Optional[Decimal] = None
    deposit: Optional[Decimal] = None
    supplier_id: Optional[int] = None
    cost: Optional[Decimal] = None
    remarks: Optional[str] = None
    deposit_due_date: Optional[date] = None
    balance_amount: Optional[Decimal] = None
    balance_due_date: Optional[date] = None


class OrderUpdate(BaseModel):
    product_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    travel_date: Optional[date] = None
    days: Optional[int] = None
    people_count: Optional[int] = None
    price: Optional[Decimal] = None
    deposit: Optional[Decimal] = None
    supplier_id: Optional[int] = None
    cost: Optional[Decimal] = None
    remarks: Optional[str] = None
    deposit_due_date: Optional[date] = None
    balance_amount: Optional[Decimal] = None
    balance_due_date: Optional[date] = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderListItem(BaseModel):
    id: int
    order_no: str
    product_id: Optional[int]
    product_name: Optional[str]
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
    deposit_due_date: Optional[date]
    balance_amount: Optional[Decimal]
    balance_due_date: Optional[date]
    created_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def get_related_names(cls, data: any) -> any:
        if hasattr(data, "product") and data.product:
            data.product_name = data.product.name
        if hasattr(data, "supplier") and data.supplier:
            data.supplier_name = data.supplier.name
        return data


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
