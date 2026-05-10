from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from app.core.deps import DBDep, require_roles, CurrentUser
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut, ResetPasswordRequest
from app.schemas.common import ResponseModel

router = APIRouter(
    prefix="/users",
    tags=["用户管理"],
    dependencies=[Depends(require_roles("admin", "system_admin"))],
)


@router.get("", response_model=ResponseModel)
async def list_users(db: DBDep, current_user: CurrentUser, role: str | None = None, status: str | None = None, keyword: str | None = None):
    stmt = select(User)
    # 系统管理员可见全部，管理员不可见系统管理员
    if current_user.role == 'admin':
        stmt = stmt.where(User.role != 'system_admin')
    if role:
        stmt = stmt.where(User.role == role)
    if status:
        stmt = stmt.where(User.status == status)
    if keyword:
        kw = f"%{keyword}%"
        from sqlalchemy import or_
        stmt = stmt.where(
            or_(User.name.ilike(kw), User.phone.ilike(kw))
        )
    result = await db.execute(stmt.order_by(User.created_at.desc()))
    users = result.scalars().all()
    return ResponseModel(data=[UserOut.model_validate(u) for u in users])


@router.get("/{user_id}", response_model=ResponseModel)
async def get_user(user_id: int, db: DBDep, current_user: CurrentUser):
    stmt = select(User)
    # 系统管理员可见全部，管理员不可见系统管理员
    if current_user.role == 'admin':
        stmt = stmt.where(User.role != 'system_admin')
    stmt = stmt.where(User.id == user_id)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ResponseModel(data=UserOut.model_validate(user))


@router.post("", response_model=ResponseModel)
async def create_user(body: UserCreate, db: DBDep, current_user: CurrentUser):
    # 管理员不能添加系统管理员
    if current_user.role == 'admin' and body.role == 'system_admin':
        raise HTTPException(status_code=403, detail="管理员无权创建系统管理员账户")
    if body.role == 'system_admin' and current_user.role != 'system_admin':
        raise HTTPException(status_code=403, detail="无权创建系统管理员账户")
    # Uniqueness checks
    # 检查手机号唯一性
    if body.phone:
        exist = await db.execute(select(User).where(User.phone == body.phone))
        if exist.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="手机号已存在")

    user = User(
        name=body.name,
        phone=body.phone,
        password=body.password,
        role=body.role,
        remark=body.remark,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return ResponseModel(data=UserOut.model_validate(user))


@router.put("/{user_id}", response_model=ResponseModel)
async def update_user(user_id: int, body: UserUpdate, db: DBDep, current_user: CurrentUser):
    stmt = select(User)
    # 系统管理员可见全部，管理员不可见系统管理员
    if current_user.role == 'admin':
        stmt = stmt.where(User.role != 'system_admin')
    stmt = stmt.where(User.id == user_id)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    for field, value in body.model_dump(exclude_none=True).items():
        if field == "phone":
            continue  # 禁止修改手机号
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return ResponseModel(data=UserOut.model_validate(user))


@router.patch("/{user_id}/status", response_model=ResponseModel)
async def toggle_user_status(user_id: int, db: DBDep, current_user: CurrentUser):
    stmt = select(User)
    # 系统管理员可见全部，管理员不可见系统管理员
    if current_user.role == 'admin':
        stmt = stmt.where(User.role != 'system_admin')
    stmt = stmt.where(User.id == user_id)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.status = "disabled" if user.status == "enabled" else "enabled"
    await db.commit()
    await db.refresh(user)
    return ResponseModel(data=UserOut.model_validate(user))


@router.post("/{user_id}/reset-password", response_model=ResponseModel)
async def reset_password(user_id: int, body: ResetPasswordRequest, db: DBDep, current_user: CurrentUser):
    stmt = select(User)
    # 系统管理员可见全部，管理员不可见系统管理员
    if current_user.role == 'admin':
        stmt = stmt.where(User.role != 'system_admin')
    stmt = stmt.where(User.id == user_id)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.password = body.password
    await db.commit()
    return ResponseModel(message="密码重置成功")
