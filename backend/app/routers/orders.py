from datetime import date
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy import select, func, or_
from app.core.deps import DBDep, CurrentUser, require_roles
from app.core.audit import write_log
from app.models.order import CustomerOrder
from app.schemas.order import OrderCreate, OrderUpdate, OrderOut, OrderListItem, OrderListResponse, OrderStatusUpdate
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/orders", tags=["客户订单"])

_STATUS_TRANSITIONS = {
    "pending_deposit": {"pending_payment"},
    "pending_payment": {"completed"},
    "completed": set(),
}


async def _gen_order_no(db) -> str:
    today = date.today()
    prefix = f"ORD-{today.strftime('%Y%m')}-"
    count_result = await db.execute(
        select(func.count(CustomerOrder.id)).where(
            CustomerOrder.order_no.like(f"{prefix}%")
        )
    )
    count = count_result.scalar_one()
    return f"{prefix}{str(count + 1).zfill(6)}"


@router.get("", response_model=ResponseModel)
async def list_orders(
    db: DBDep,
    _: CurrentUser,
    status: str | None = None,
    keyword: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(CustomerOrder)
    if status:
        stmt = stmt.where(CustomerOrder.status == status)
    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                CustomerOrder.customer_name.ilike(kw),
                CustomerOrder.order_no.ilike(kw),
                CustomerOrder.product_name.ilike(kw),
            )
        )
    if start_date:
        stmt = stmt.where(CustomerOrder.travel_date >= start_date)
    if end_date:
        stmt = stmt.where(CustomerOrder.travel_date <= end_date)

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar_one()

    stmt = stmt.order_by(CustomerOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(stmt)).scalars().all()

    return ResponseModel(data=OrderListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[OrderListItem.model_validate(o) for o in rows],
    ))


@router.get("/{order_id}", response_model=ResponseModel)
async def get_order(order_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(CustomerOrder).where(CustomerOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return ResponseModel(data=OrderOut.model_validate(order))


@router.post("", response_model=ResponseModel, status_code=201)
async def create_order(body: OrderCreate, db: DBDep, user: CurrentUser, request: Request):
    order_no = await _gen_order_no(db)
    profit = None
    if body.price is not None and body.cost is not None:
        profit = body.price - body.cost

    order = CustomerOrder(
        **body.model_dump(),
        order_no=order_no,
        profit=profit,
        status="pending_deposit",
        created_by=user.id,
    )
    db.add(order)
    await db.flush()
    await write_log(
        db, user.id, user.full_name,
        action="create_order",
        resource_type="order",
        resource_id=str(order.id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(order)
    return ResponseModel(data=OrderOut.model_validate(order))


@router.put("/{order_id}", response_model=ResponseModel)
async def update_order(order_id: int, body: OrderUpdate, db: DBDep, user: CurrentUser, request: Request):
    result = await db.execute(select(CustomerOrder).where(CustomerOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    if order.price is not None and order.cost is not None:
        order.profit = order.price - order.cost

    await db.flush()
    await write_log(
        db, user.id, user.full_name,
        action="update_order",
        resource_type="order",
        resource_id=str(order_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(order)
    return ResponseModel(data=OrderOut.model_validate(order))


@router.patch(
    "/{order_id}/status",
    response_model=ResponseModel,
    dependencies=[Depends(require_roles("admin", "system_admin"))],
)
async def update_order_status(order_id: int, body: OrderStatusUpdate, db: DBDep, user: CurrentUser, request: Request):
    result = await db.execute(select(CustomerOrder).where(CustomerOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    allowed = _STATUS_TRANSITIONS.get(order.status, set())
    if body.status not in allowed:
        raise HTTPException(status_code=422, detail=f"无法从 {order.status} 转为 {body.status}")

    old_status = order.status
    order.status = body.status
    await db.flush()
    await write_log(
        db, user.id, user.full_name,
        action="update_order_status",
        resource_type="order",
        resource_id=str(order_id),
        detail=f"{old_status} → {body.status}",
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(order)
    return ResponseModel(data=OrderOut.model_validate(order))


@router.delete(
    "/{order_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_roles("admin", "system_admin"))],
)
async def delete_order(order_id: int, db: DBDep, user: CurrentUser, request: Request):
    result = await db.execute(select(CustomerOrder).where(CustomerOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    await write_log(
        db, user.id, user.full_name,
        action="delete_order",
        resource_type="order",
        resource_id=str(order_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.delete(order)
    await db.commit()
    return ResponseModel(message="删除成功")



@router.get("", response_model=ResponseModel)
async def list_all_orders(
    db: DBDep,
    _: CurrentUser,
    status: str | None = None,
    service_type: str | None = None,
    itinerary_id: int | None = None,
    page: int = 1,
    page_size: int = 50,
):
    stmt = (
        select(Order)
        .options(selectinload(Order.itinerary))
        .join(Order.itinerary)
    )
    if status:
        stmt = stmt.where(Order.status == status)
    if service_type:
        stmt = stmt.where(Order.service_type == service_type)
    if itinerary_id:
        stmt = stmt.where(Order.itinerary_id == itinerary_id)
    stmt = stmt.order_by(Order.order_date.desc()).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    orders = result.scalars().all()

    # Bulk-load supplier names
    supplier_ids = {o.supplier_id for o in orders if o.supplier_id}
    supplier_map: dict[int, str] = {}
    if supplier_ids:
        sup_res = await db.execute(select(Supplier).where(Supplier.id.in_(supplier_ids)))
        supplier_map = {s.id: s.name for s in sup_res.scalars().all()}

    data = [
        OrderListOut(
            id=o.id,
            itinerary_id=o.itinerary_id,
            itinerary_name=o.itinerary.name,
            supplier_id=o.supplier_id,
            supplier_name=supplier_map.get(o.supplier_id) if o.supplier_id else None,
            service_type=o.service_type,
            amount=o.amount,
            order_date=o.order_date,
            status=o.status,
            notes=o.notes,
            created_at=o.created_at,
        )
        for o in orders
    ]
    return ResponseModel(data=data)


@router.patch("/{order_id}/status", response_model=ResponseModel)
async def update_order_status(order_id: int, new_status: str, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="订单不存在")
    order.status = new_status
    await db.commit()
    return ResponseModel(message="状态已更新")
