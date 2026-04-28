from datetime import timedelta
import secrets
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.deps import DBDep, CurrentUser
from app.core.audit import write_log
from app.models.itinerary import Itinerary, ItineraryDay, Order
from app.schemas.itinerary import (
    ItineraryCreate, ItineraryUpdate, ItineraryOut, ItineraryListItem,
    OrderCreate, OrderUpdate, OrderOut, ItineraryStatusUpdate, ShareTokenResponse,
)
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/itineraries", tags=["行程"])
public_router = APIRouter(prefix="/public/itineraries", tags=["行程公开分享"])

_LOAD_FULL = [
    selectinload(Itinerary.days_detail).selectinload(ItineraryDay.attachments),
    selectinload(Itinerary.orders).selectinload(Order.attachments),
]

VALID_TRANSITIONS = {
    "not_started": {"in_progress", "cancelled"},
    "in_progress":  {"completed"},
    # "completed":    {"in_progress"},  # 已移除撤销完成回退
}


async def _get_itinerary(itinerary_id: int, db: DBDep) -> Itinerary:
    result = await db.execute(
        select(Itinerary).where(Itinerary.id == itinerary_id).options(*_LOAD_FULL)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="行程不存在")
    return obj


@router.get("", response_model=ResponseModel)
async def list_itineraries(
    db: DBDep,
    _: CurrentUser,
    status: str | None = None,
    customer_name: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    stmt = select(Itinerary)
    if status:
        stmt = stmt.where(Itinerary.status == status)
    if customer_name:
        stmt = stmt.where(Itinerary.customer_name.ilike(f"%{customer_name}%"))
    stmt = stmt.order_by(Itinerary.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ResponseModel(data=[ItineraryListItem.model_validate(i) for i in items])


@router.post("", response_model=ResponseModel)
async def create_itinerary(body: ItineraryCreate, db: DBDep, user: CurrentUser, request: Request):
    # Enforce unique customer_order_id
    if body.customer_order_id:
        conflict = await db.execute(
            select(Itinerary).where(Itinerary.customer_order_id == body.customer_order_id)
        )
        if conflict.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="该订单已关联行程")

    days_data = body.model_dump(exclude={"days_detail"})
    itinerary = Itinerary(**{k: v for k, v in days_data.items()})
    itinerary.created_by = user.id

    for day in body.days_detail:
        itinerary.days_detail.append(ItineraryDay(**day.model_dump()))

    db.add(itinerary)
    await db.flush()
    await write_log(
        db, user.id, user.full_name,
        action="create_itinerary",
        resource_type="itinerary",
        resource_id=str(itinerary.id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(itinerary)
    full = await _get_itinerary(itinerary.id, db)
    return ResponseModel(data=ItineraryOut.model_validate(full))


@router.get("/{itinerary_id}", response_model=ResponseModel)
async def get_itinerary(itinerary_id: int, db: DBDep, _: CurrentUser):
    return ResponseModel(data=ItineraryOut.model_validate(await _get_itinerary(itinerary_id, db)))


@router.put("/{itinerary_id}", response_model=ResponseModel)
async def update_itinerary(itinerary_id: int, body: ItineraryUpdate, db: DBDep, user: CurrentUser, request: Request):
    itinerary = await _get_itinerary(itinerary_id, db)
    if itinerary.status == "completed":
        raise HTTPException(status_code=400, detail="已完成的行程不可编辑")

    data = body.model_dump(exclude_none=True, exclude={"days_detail"})
    for field, value in data.items():
        setattr(itinerary, field, value)

    if body.days_detail is not None:
        for day in itinerary.days_detail:
            await db.delete(day)
        for day in body.days_detail:
            itinerary.days_detail.append(ItineraryDay(**day.model_dump(), itinerary_id=itinerary_id))

    await db.flush()
    await write_log(
        db, user.id, user.full_name,
        action="update_itinerary",
        resource_type="itinerary",
        resource_id=str(itinerary_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    full = await _get_itinerary(itinerary_id, db)
    return ResponseModel(data=ItineraryOut.model_validate(full))


@router.patch("/{itinerary_id}/status", response_model=ResponseModel)
async def update_status(itinerary_id: int, body: ItineraryStatusUpdate, db: DBDep, user: CurrentUser, request: Request):
    itinerary = await _get_itinerary(itinerary_id, db)
    if body.status not in VALID_TRANSITIONS.get(itinerary.status, set()):
        raise HTTPException(status_code=400, detail=f"不能从 {itinerary.status} 流转至 {body.status}")
    itinerary.status = body.status
    await db.flush()
    await write_log(
        db, user.id, user.full_name,
        action="update_itinerary_status",
        resource_type="itinerary",
        resource_id=str(itinerary_id),
        detail=body.status,
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    return ResponseModel(data={"status": body.status})


@router.post("/{itinerary_id}/share", response_model=ResponseModel)
async def share_itinerary(itinerary_id: int, db: DBDep, user: CurrentUser, request: Request):
    itinerary = await _get_itinerary(itinerary_id, db)
    if not itinerary.share_token:
        itinerary.share_token = secrets.token_urlsafe(32)
    await db.flush()
    await write_log(
        db, user.id, user.full_name,
        action="share_itinerary",
        resource_type="itinerary",
        resource_id=str(itinerary_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    return ResponseModel(data=ShareTokenResponse(
        share_token=itinerary.share_token,
        share_url=f"/public/itineraries/{itinerary.share_token}",
    ))


@router.delete("/{itinerary_id}/share", response_model=ResponseModel)
async def revoke_itinerary_share(itinerary_id: int, db: DBDep, user: CurrentUser, request: Request):
    itinerary = await _get_itinerary(itinerary_id, db)
    itinerary.share_token = None
    await db.flush()
    await write_log(
        db, user.id, user.full_name,
        action="revoke_itinerary_share",
        resource_type="itinerary",
        resource_id=str(itinerary_id),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    return ResponseModel(message="分享链接已撤销")


@router.post("/{itinerary_id}/copy", response_model=ResponseModel)
async def copy_itinerary(itinerary_id: int, db: DBDep, user: CurrentUser):
    src = await _get_itinerary(itinerary_id, db)
    new_itin = Itinerary(
        name=f"{src.name}（复制）",
        origin=src.origin,
        destination=src.destination,
        days=src.days,
        departure_date=src.departure_date,
        tags=src.tags,
        notes=src.notes,
        customer_name="",
        customer_phone="",
        pax=src.pax,
        status="draft",
        created_by=user.id,
    )
    for day in src.days_detail:
        new_itin.days_detail.append(ItineraryDay(
            day_number=day.day_number,
            date=day.date,
            details=day.details,
            accommodation_area=day.accommodation_area,
            notes=day.notes,
        ))
    db.add(new_itin)
    await db.commit()
    await db.refresh(new_itin)
    return ResponseModel(data={"id": new_itin.id})


@router.delete("/{itinerary_id}", response_model=ResponseModel)
async def delete_itinerary(itinerary_id: int, db: DBDep, _: CurrentUser):
    itinerary = await _get_itinerary(itinerary_id, db)
    await db.delete(itinerary)
    await db.commit()
    return ResponseModel(message="删除成功")


# ── 订单子路由 ─────────────────────────────────────────────────────

@router.get("/{itinerary_id}/orders", response_model=ResponseModel)
async def list_orders(itinerary_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(
        select(Order).where(Order.itinerary_id == itinerary_id)
        .options(selectinload(Order.attachments))
        .order_by(Order.order_date)
    )
    return ResponseModel(data=[OrderOut.model_validate(o) for o in result.scalars().all()])


@router.post("/{itinerary_id}/orders", response_model=ResponseModel)
async def create_order(itinerary_id: int, body: OrderCreate, db: DBDep, user: CurrentUser):
    order = Order(**body.model_dump(), itinerary_id=itinerary_id, created_by=user.id)
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return ResponseModel(data=OrderOut.model_validate(order))


@router.put("/{itinerary_id}/orders/{order_id}", response_model=ResponseModel)
async def update_order(itinerary_id: int, order_id: int, body: OrderUpdate, db: DBDep, _: CurrentUser):
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.itinerary_id == itinerary_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(order, field, value)
    await db.commit()
    return ResponseModel(data=OrderOut.model_validate(order))


@router.delete("/{itinerary_id}/orders/{order_id}", response_model=ResponseModel)
async def delete_order(itinerary_id: int, order_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.itinerary_id == itinerary_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    await db.delete(order)
    await db.commit()
    return ResponseModel(message="删除成功")


# ── 公开分享路由 ────────────────────────────────────────────────────

@public_router.get("/{share_token}", response_model=ResponseModel)
async def get_public_itinerary(share_token: str, db: DBDep):
    result = await db.execute(
        select(Itinerary).where(Itinerary.share_token == share_token).options(*_LOAD_FULL)
    )
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(status_code=404, detail="分享链接无效")
    return ResponseModel(data=ItineraryOut.model_validate(itinerary))
