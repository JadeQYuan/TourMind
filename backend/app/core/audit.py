"""Audit log writer — call after a successful DB operation (before the outer commit)."""
import json
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


async def write_log(
    db: AsyncSession,
    request_or_user_id: Any,
    user_or_name: Any,
    resource_type_or_action: Optional[str] = None,
    resource_id_or_resource_type: Optional[Any] = None,
    action_or_resource_id: Optional[str] = None,
    detail: Optional[Any] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Flexible audit log writer.

    Supports two call conventions:
    1. New-style: write_log(db, request, user_obj, resource_type, resource_id, action, detail_dict)
    2. Old-style: write_log(db, user_id, user_name, action, resource_type, resource_id, detail_str, ip)
    """
    from fastapi import Request as FastAPIRequest

    if isinstance(request_or_user_id, FastAPIRequest):
        # New-style call: (db, request, user_obj, resource_type, resource_id, action, detail_dict)
        request = request_or_user_id
        user = user_or_name
        resource_type = resource_type_or_action
        resource_id = resource_id_or_resource_type
        action = action_or_resource_id
        detail_val = json.dumps(detail, ensure_ascii=False, default=str) if isinstance(detail, dict) else detail
        user_id = getattr(user, 'id', None)
        user_name = getattr(user, 'full_name', None) or getattr(user, 'username', None) or str(user_id)
        ip = request.client.host if request.client else None
    else:
        # Old-style call: (db, user_id, user_name, action, resource_type, resource_id, detail, ip)
        user_id = request_or_user_id
        user_name = user_or_name
        action = resource_type_or_action
        resource_type = resource_id_or_resource_type
        resource_id = action_or_resource_id
        detail_val = detail
        ip = ip_address

    entry = AuditLog(
        user_id=user_id,
        user_name=user_name,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        detail=detail_val,
        ip_address=ip,
    )
    db.add(entry)
    await db.flush()
