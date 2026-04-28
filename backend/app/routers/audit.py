from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_
from datetime import date
from app.core.deps import DBDep, require_roles
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogListResponse, AuditLogOut

router = APIRouter(
    prefix="/audit-logs",
    tags=["审计日志"],
    dependencies=[Depends(require_roles("system_admin"))],
)


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    db: DBDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: int | None = None,
    resource_type: str | None = None,
    action: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    keyword: str | None = None,
):
    stmt = select(AuditLog)

    if user_id is not None:
        stmt = stmt.where(AuditLog.user_id == user_id)
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if start_date:
        stmt = stmt.where(AuditLog.created_at >= start_date)
    if end_date:
        from datetime import datetime, timedelta
        end_dt = datetime.combine(end_date, datetime.max.time())
        stmt = stmt.where(AuditLog.created_at <= end_dt)
    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                AuditLog.user_name.ilike(kw),
                AuditLog.action.ilike(kw),
                AuditLog.resource_type.ilike(kw),
                AuditLog.detail.ilike(kw),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    stmt = stmt.order_by(AuditLog.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return AuditLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[AuditLogOut.model_validate(item) for item in items],
    )
