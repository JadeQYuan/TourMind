from pydantic import BaseModel, model_validator
from datetime import date, datetime
from decimal import Decimal
from typing import Literal


BillType = Literal["income", "expense"]
IncomeType = Literal["deposit", "balance", "full", "other"]
ExpenseType = Literal[
    "transport", "accommodation", "attraction", "meal",
    "guide", "insurance", "operation", "other"
]


class BillCreate(BaseModel):
    contract_id: int | None = None
    order_id: int | None = None
    bill_type: BillType
    income_type: IncomeType | None = None
    expense_type: ExpenseType | None = None
    supplier_id: int | None = None
    amount: Decimal
    bill_date: date
    account_id: int
    notes: str | None = None
    attachment_url: str | None = None

    @model_validator(mode="after")
    def check_type_fields(self) -> "BillCreate":
        if self.bill_type == "income" and not self.income_type:
            raise ValueError("入账必须填写 income_type")
        if self.bill_type == "expense" and not self.expense_type:
            raise ValueError("出账必须填写 expense_type")
        return self


class BillUpdate(BaseModel):
    amount: Decimal | None = None
    bill_date: date | None = None
    account_id: int | None = None
    notes: str | None = None
    attachment_url: str | None = None
    income_type: IncomeType | None = None
    expense_type: ExpenseType | None = None
    supplier_id: int | None = None


class BillOut(BaseModel):
    id: int
    contract_id: int | None
    order_id: int | None
    bill_type: str
    income_type: str | None
    expense_type: str | None
    supplier_id: int | None
    amount: Decimal
    bill_date: date
    account_id: int
    notes: str | None
    attachment_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    month_income: Decimal
    month_expense: Decimal
    month_profit: Decimal
    pending_income: Decimal
