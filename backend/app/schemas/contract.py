from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Literal


ContractStatus = Literal[
    "pending_sign", "signed", "revoked"
]


class ContractDayCreate(BaseModel):
    day_number: int
    date: date
    details: str = ""
    accommodation_area: str | None = None
    notes: str | None = None


class ContractDayOut(BaseModel):
    id: int
    day_number: int
    date: date
    details: str
    accommodation_area: str | None
    notes: str | None

    model_config = {"from_attributes": True}


class ContractCreate(BaseModel):
    source_itinerary_id: int | None = None
    order_id: int | None = None
    # 费用条款
    total_amount: Decimal
    price_per_person: Decimal | None = None
    deposit_amount: Decimal | None = None
    deposit_due_date: date | None = None
    balance_due_date: date | None = None
    includes: str | None = None
    excludes: str | None = None
    cancellation_policy: str | None = None
    travel_notice: str | None = None
    notes: str | None = None
    # 甲乙方及联系电话
    party_a: str | None = None
    party_a_phone: str | None = None
    party_b: str | None = None
    party_b_phone: str | None = None
    # 行程明细快照（从行程导入后可微调）
    days_detail: list[ContractDayCreate] = []


class ContractUpdate(BaseModel):
    total_amount: Decimal | None = None
    price_per_person: Decimal | None = None
    deposit_amount: Decimal | None = None
    deposit_due_date: date | None = None
    balance_due_date: date | None = None
    includes: str | None = None
    excludes: str | None = None
    cancellation_policy: str | None = None
    travel_notice: str | None = None
    notes: str | None = None
    days_detail: list[ContractDayCreate] | None = None
    party_a: str | None = None
    party_a_phone: str | None = None
    party_b: str | None = None
    party_b_phone: str | None = None


class ContractStatusUpdate(BaseModel):
    status: ContractStatus
    cancel_reason: str | None = None


class ContractListItem(BaseModel):
    id: int
    contract_no: str
    customer_name: str
    departure_date: date
    total_amount: Decimal
    status: str
    order_id: int | None
    share_token: str | None
    signed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BillSummary(BaseModel):
    total_amount: Decimal
    total_income: Decimal
    pending_income: Decimal
    total_expense: Decimal
    estimated_profit: Decimal


class ContractOut(BaseModel):
    id: int
    contract_no: str
    order_id: int | None
    source_itinerary_id: int | None
    customer_name: str
    customer_phone: str
    pax: int
    travelers: list | None
    departure_date: date
    return_date: date
    total_amount: Decimal
    price_per_person: Decimal | None
    deposit_amount: Decimal | None
    deposit_due_date: date | None
    balance_amount: Decimal | None
    balance_due_date: date | None
    includes: str | None
    excludes: str | None
    cancellation_policy: str | None
    travel_notice: str | None
    status: str
    cancel_reason: str | None
    share_token: str | None
    signed_at: datetime | None
    notes: str | None
    party_a: str | None
    party_a_phone: str | None
    party_b: str | None
    party_b_phone: str | None
    created_at: datetime
    updated_at: datetime
    days_detail: list[ContractDayOut] = []
    bill_summary: BillSummary | None = None

    model_config = {"from_attributes": True}


# ── 客户端签署 ─────────────────────────────────────────────────────

class ContractPublicOut(BaseModel):
    """外部分享页使用，不含敏感内部信息"""
    contract_no: str
    customer_name: str
    departure_date: date
    return_date: date
    total_amount: Decimal
    deposit_amount: Decimal | None
    deposit_due_date: date | None
    balance_amount: Decimal | None
    balance_due_date: date | None
    includes: str | None
    excludes: str | None
    cancellation_policy: str | None
    travel_notice: str | None
    status: str
    days_detail: list[ContractDayOut] = []

    model_config = {"from_attributes": True}


class PhoneVerifyRequest(BaseModel):
    phone: str


class IdDocumentItem(BaseModel):
    name: str
    id_type: Literal["id_card", "passport", "hk_pass"]
    id_no: str
    front_url: str
    back_url: str | None = None


class ContractSignRequest(BaseModel):
    signature_image_url: str          # base64 data URL 或上传后的文件 URL
    id_documents: list[IdDocumentItem]
