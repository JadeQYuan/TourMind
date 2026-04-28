import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select, func as sqlfunc
from sqlalchemy.orm import selectinload
from app.core.deps import DBDep, CurrentUser
from app.core.audit import write_log
from app.models.contract import Contract, ContractDay
from app.models.itinerary import Itinerary
from app.models.bill import Bill
from app.schemas.contract import (
    ContractCreate, ContractUpdate, ContractOut, ContractListItem,
    ContractStatusUpdate, ContractPublicOut,
    PhoneVerifyRequest, ContractSignRequest,
    BillSummary,
)
from app.schemas.common import ResponseModel
from decimal import Decimal

router = APIRouter(prefix="/contracts", tags=["合同"])

CONTRACT_TRANSITIONS = {
    "pending_sign": {"signed", "revoked"},
    "signed": {"revoked"},
    "revoked": set(),
}

_LOAD_FULL = [selectinload(Contract.days_detail)]


async def _get_contract(contract_id: int, db: DBDep) -> Contract:
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id).options(*_LOAD_FULL)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="合同不存在")
    return obj


async def _bill_summary(contract_id: int, total_amount: Decimal, db: DBDep) -> BillSummary:
    result = await db.execute(
        select(Bill.bill_type, sqlfunc.sum(Bill.amount))
        .where(Bill.contract_id == contract_id)
        .group_by(Bill.bill_type)
    )
    rows = {row[0]: row[1] or Decimal(0) for row in result.all()}
    total_income = rows.get("income", Decimal(0))
    total_expense = rows.get("expense", Decimal(0))
    return BillSummary(
        total_amount=total_amount,
        total_income=total_income,
        pending_income=max(total_amount - total_income, Decimal(0)),
        total_expense=total_expense,
        estimated_profit=total_income - total_expense,
    )


def _next_contract_no() -> str:
    from datetime import date
    return f"TRV-{date.today().strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"


@router.get("", response_model=ResponseModel)
async def list_contracts(
    db: DBDep,
    _: CurrentUser,
    status: str | None = None,
    customer_name: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    stmt = select(Contract)
    if status:
        stmt = stmt.where(Contract.status == status)
    if customer_name:
        stmt = stmt.where(Contract.customer_name.ilike(f"%{customer_name}%"))
    stmt = stmt.order_by(Contract.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return ResponseModel(data=[ContractListItem.model_validate(c) for c in result.scalars().all()])


@router.post("", response_model=ResponseModel)
async def create_contract(request: Request, body: ContractCreate, db: DBDep, user: CurrentUser):
        # 参数校验
        if not body.customer_order_id:
            raise HTTPException(status_code=422, detail="customer_order_id 必填")
        if not body.party_a or not body.party_a_phone or not body.party_b or not body.party_b_phone:
            raise HTTPException(status_code=422, detail="甲乙方及联系方式必填")
    # Auto-populate from CustomerOrder if provided
    customer_name = ""
    customer_phone = ""
    pax = 1
    travelers = None
    departure_date = None
    return_date = None

    party_a = body.party_a
    party_a_phone = body.party_a_phone
    party_b = body.party_b
    party_b_phone = body.party_b_phone

    if body.customer_order_id:
        from app.models.order import CustomerOrder
        order_res = await db.execute(
            select(CustomerOrder).where(CustomerOrder.id == body.customer_order_id)
        )
        order = order_res.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="关联订单不存在")
        customer_name = order.customer_name
        customer_phone = order.customer_phone
        pax = order.people_count or 1
        departure_date = order.travel_date
        return_date = order.travel_date  # caller can update via PUT
        # 行程明细通过订单接口获取，接口防御性校验
        try:
            from app.models.itinerary import Itinerary
            itin_result = await db.execute(
                select(Itinerary).where(Itinerary.customer_order_id == order.id)
            )
            itins = itin_result.scalars().all()
            if not itins:
                raise HTTPException(status_code=400, detail="订单未关联行程，无法创建合同")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"行程明细获取失败: {e}")
        # 自动填充甲方及电话
        if party_a is None:
            party_a = order.customer_name
        if party_a_phone is None:
            party_a_phone = order.customer_phone
        if party_b is None:
            party_b = "旅行社"
        if party_b_phone is None:
            party_b_phone = "0755-12345678"
    elif body.source_itinerary_id:
        # Legacy: populate from itinerary
        itin_result = await db.execute(
            select(Itinerary).where(Itinerary.id == body.source_itinerary_id)
        )
        itin = itin_result.scalar_one_or_none()
        if not itin:
            raise HTTPException(status_code=404, detail="行程不存在")
        customer_name = itin.customer_name
        customer_phone = itin.customer_phone
        pax = itin.pax
        travelers = itin.travelers
        departure_date = itin.departure_date
        from datetime import timedelta
        return_date = itin.departure_date + timedelta(days=(itin.days or 1) - 1)
    else:
        raise HTTPException(status_code=400, detail="必须提供 customer_order_id 或 source_itinerary_id")

    if not departure_date:
        raise HTTPException(status_code=400, detail="无法确定出发日期")

    balance = body.total_amount - (body.deposit_amount or Decimal(0))

    contract = Contract(
        contract_no=_next_contract_no(),
        customer_order_id=body.customer_order_id,
        source_itinerary_id=body.source_itinerary_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        pax=pax,
        travelers=travelers,
        departure_date=departure_date,
        return_date=return_date,
        total_amount=body.total_amount,
        price_per_person=body.price_per_person,
        deposit_amount=body.deposit_amount,
        deposit_due_date=body.deposit_due_date,
        balance_amount=balance if body.deposit_amount else None,
        balance_due_date=body.balance_due_date,
        includes=body.includes,
        excludes=body.excludes,
        cancellation_policy=body.cancellation_policy,
        travel_notice=body.travel_notice,
        notes=body.notes,
        party_a=party_a,
        party_a_phone=party_a_phone,
        party_b=party_b,
        party_b_phone=party_b_phone,
        status="pending_sign",
        share_token=secrets.token_urlsafe(32),
        created_by=user.id,
    )
    for day in body.days_detail:
        contract.days_detail.append(ContractDay(**day.model_dump()))

    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    await write_log(db, request, user, "contract", contract.id, "create", {"contract_no": contract.contract_no})
    return ResponseModel(data=ContractListItem.model_validate(contract))


@router.get("/{contract_id}", response_model=ResponseModel)
async def get_contract(contract_id: int, db: DBDep, _: CurrentUser):
    contract = await _get_contract(contract_id, db)
    out = ContractOut.model_validate(contract)
    out.bill_summary = await _bill_summary(contract_id, contract.total_amount, db)
    # 确保新字段返回
    out.party_a = contract.party_a
    out.party_a_phone = contract.party_a_phone
    out.party_b = contract.party_b
    out.party_b_phone = contract.party_b_phone
    return ResponseModel(data=out)


@router.put("/{contract_id}", response_model=ResponseModel)
async def update_contract(request: Request, contract_id: int, body: ContractUpdate, db: DBDep, user: CurrentUser):
        # 参数校验
        if not body.party_a or not body.party_a_phone or not body.party_b or not body.party_b_phone:
            raise HTTPException(status_code=422, detail="甲乙方及联系方式必填")
        if not contract.customer_order_id:
            raise HTTPException(status_code=422, detail="customer_order_id 必填")
    contract = await _get_contract(contract_id, db)
    if contract.status not in ("pending_sign",):
        raise HTTPException(status_code=400, detail="仅待签署状态可编辑")

    data = body.model_dump(exclude_none=True, exclude={"days_detail"})
    for field, value in data.items():
        setattr(contract, field, value)

    if body.days_detail is not None:
        for d in contract.days_detail:
            await db.delete(d)
        for day in body.days_detail:
            contract.days_detail.append(ContractDay(**day.model_dump(), contract_id=contract_id))

    await db.commit()
    await write_log(db, request, user, "contract", contract_id, "update", {})
    return ResponseModel(data=ContractListItem.model_validate(contract))


@router.patch("/{contract_id}/status", response_model=ResponseModel)
async def update_status(request: Request, contract_id: int, body: ContractStatusUpdate, db: DBDep, user: CurrentUser):
    contract = await _get_contract(contract_id, db)
    allowed = CONTRACT_TRANSITIONS.get(contract.status, set())
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail=f"不能从 {contract.status} 流转至 {body.status}")

    if body.status == "revoked":
        if not body.cancel_reason:
            raise HTTPException(status_code=400, detail="取消时必须填写原因")
        contract.cancel_reason = body.cancel_reason
        contract.share_token = None

    contract.status = body.status
    await db.commit()
    await write_log(db, request, user, "contract", contract_id, "status_change", {"status": body.status})
    return ResponseModel(data={"status": contract.status})


@router.post("/{contract_id}/share", response_model=ResponseModel)
async def share_contract(request: Request, contract_id: int, db: DBDep, user: CurrentUser):
    contract = await _get_contract(contract_id, db)
    if contract.status == "revoked":
        raise HTTPException(status_code=400, detail="已撤销的合同不能分享")
    token = secrets.token_urlsafe(32)
    contract.share_token = token
    if contract.status == "draft":
        contract.status = "pending_sign"
    await db.commit()
    await write_log(db, request, user, "contract", contract_id, "share", {})
    return ResponseModel(data={"share_token": token})


@router.delete("/{contract_id}/share", response_model=ResponseModel)
async def revoke_share(request: Request, contract_id: int, db: DBDep, user: CurrentUser):
    contract = await _get_contract(contract_id, db)
    contract.share_token = None
    await db.commit()
    await write_log(db, request, user, "contract", contract_id, "revoke_share", {})
    return ResponseModel(message="分享已撤销")


# ── 外部签署端点（无需登录） ────────────────────────────────────────

public_router = APIRouter(prefix="/public/contracts", tags=["合同签署（外部）"])


@public_router.get("/{token}", response_model=ResponseModel)
async def get_contract_by_token(token: str, db: DBDep):
    result = await db.execute(
        select(Contract).where(Contract.share_token == token).options(*_LOAD_FULL)
    )
    contract = result.scalar_one_or_none()
    if not contract or contract.status not in ("pending_sign",):
        raise HTTPException(status_code=404, detail="签署链接无效或已过期")
    return ResponseModel(data=ContractPublicOut.model_validate(contract))


@public_router.post("/{token}/verify-phone", response_model=ResponseModel)
async def verify_phone(token: str, body: PhoneVerifyRequest, db: DBDep):
    result = await db.execute(select(Contract).where(Contract.share_token == token))
    contract = result.scalar_one_or_none()
    if not contract or contract.status != "pending_sign":
        raise HTTPException(status_code=404, detail="签署链接无效")
    if contract.customer_phone != body.phone:
        raise HTTPException(status_code=400, detail="手机号与预留信息不符，请联系旅行社")
    return ResponseModel(message="验证成功")


@public_router.post("/{token}/sign", response_model=ResponseModel)
async def sign_contract(token: str, body: ContractSignRequest, db: DBDep):
    result = await db.execute(
        select(Contract).where(Contract.share_token == token)
    )
    contract = result.scalar_one_or_none()
    if not contract or contract.status != "pending_sign":
        raise HTTPException(status_code=404, detail="签署链接无效")

    contract.signature_image_url = body.signature_image_url
    contract.id_documents = [doc.model_dump() for doc in body.id_documents]
    contract.signed_at = datetime.now(timezone.utc)
    contract.status = "signed"
    contract.share_token = None  # 签署完成后令牌失效

    await db.commit()
    return ResponseModel(message="签署成功")
