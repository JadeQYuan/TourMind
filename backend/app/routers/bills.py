from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select, func as sqlfunc, extract
from datetime import date
from decimal import Decimal
from app.core.deps import DBDep, CurrentUser
from app.core.audit import write_log
from app.models.bill import Bill
from app.models.contract import Contract
from app.schemas.bill import BillCreate, BillUpdate, BillOut, DashboardSummary
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/bills", tags=["账单"])


@router.get("/summary", response_model=ResponseModel)
async def dashboard_summary(db: DBDep, _: CurrentUser):
    today = date.today()
    result = await db.execute(
        select(Bill.bill_type, sqlfunc.sum(Bill.amount))
        .where(
            extract("year", Bill.bill_date) == today.year,
            extract("month", Bill.bill_date) == today.month,
        )
        .group_by(Bill.bill_type)
    )
    rows = {row[0]: row[1] or Decimal(0) for row in result.all()}
    income = rows.get("income", Decimal(0))
    expense = rows.get("expense", Decimal(0))

    # 待收款：所有合同总金额 - 已入账金额
    pending_result = await db.execute(
        select(
            sqlfunc.coalesce(sqlfunc.sum(Contract.total_amount), Decimal(0)),
        ).where(Contract.status.in_(["signed", "in_progress"]))
    )
    total_contract = pending_result.scalar() or Decimal(0)
    income_result = await db.execute(
        select(sqlfunc.coalesce(sqlfunc.sum(Bill.amount), Decimal(0)))
        .where(Bill.bill_type == "income", Bill.contract_id.isnot(None))
    )
    total_income = income_result.scalar() or Decimal(0)

    return ResponseModel(data=DashboardSummary(
        month_income=income,
        month_expense=expense,
        month_profit=income - expense,
        pending_income=max(total_contract - total_income, Decimal(0)),
    ))


@router.get("", response_model=ResponseModel)
async def list_bills(
    db: DBDep,
    _: CurrentUser,
    bill_type: str | None = None,
    contract_id: int | None = None,
    customer_order_id: int | None = None,
    account_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
):
    stmt = select(Bill)
    if bill_type:
        stmt = stmt.where(Bill.bill_type == bill_type)
    if contract_id:
        stmt = stmt.where(Bill.contract_id == contract_id)
    if customer_order_id:
        stmt = stmt.where(Bill.customer_order_id == customer_order_id)
    if account_id:
        stmt = stmt.where(Bill.account_id == account_id)
    if start_date:
        stmt = stmt.where(Bill.bill_date >= start_date)
    if end_date:
        stmt = stmt.where(Bill.bill_date <= end_date)
    stmt = stmt.order_by(Bill.bill_date.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return ResponseModel(data=[BillOut.model_validate(b) for b in result.scalars().all()])


@router.post("", response_model=ResponseModel)
async def create_bill(request: Request, body: BillCreate, db: DBDep, user: CurrentUser):
    bill = Bill(**body.model_dump(), created_by=user.id)
    db.add(bill)
    await db.commit()
    await db.refresh(bill)
    await write_log(db, request, user, "bill", bill.id, "create", {"amount": str(bill.amount), "type": bill.bill_type})
    return ResponseModel(data=BillOut.model_validate(bill))


@router.get("/{bill_id}", response_model=ResponseModel)
async def get_bill(bill_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    return ResponseModel(data=BillOut.model_validate(bill))


@router.put("/{bill_id}", response_model=ResponseModel)
async def update_bill(request: Request, bill_id: int, body: BillUpdate, db: DBDep, user: CurrentUser):
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(bill, field, value)
    await db.commit()
    await write_log(db, request, user, "bill", bill_id, "update", {})
    return ResponseModel(data=BillOut.model_validate(bill))


@router.delete("/{bill_id}", response_model=ResponseModel)
async def delete_bill(request: Request, bill_id: int, db: DBDep, user: CurrentUser):
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    await db.delete(bill)
    await db.commit()
    await write_log(db, request, user, "bill", bill_id, "delete", {})
    return ResponseModel(message="删除成功")
