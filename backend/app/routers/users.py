import secrets
import string
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from app.core.deps import DBDep, require_roles, CurrentUser
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut, UserCreateResponse, ResetPasswordResponse
from app.schemas.common import ResponseModel

router = APIRouter(
    prefix="/users",
    tags=["用户管理"],
    dependencies=[Depends(require_roles("admin", "system_admin"))],
)


def _gen_password(length: int = 12) -> str:
    """Generate a random password that satisfies complexity requirements."""
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*"
    # Guarantee at least one of each category
    parts = [
        secrets.choice(upper),
        secrets.choice(lower),
        secrets.choice(digits),
        secrets.choice(special),
    ]
    alphabet = upper + lower + digits + special
    parts += [secrets.choice(alphabet) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(parts)
    return "".join(parts)


@router.get("", response_model=ResponseModel)
async def list_users(db: DBDep, current_user: CurrentUser, role: str | None = None, is_active: bool | None = None, keyword: str | None = None):
    stmt = select(User)
    # 系统管理员可见全部，管理员不可见系统管理员
    if current_user.role == 'admin':
        stmt = stmt.where(User.role != 'system_admin')
    if role:
        stmt = stmt.where(User.role == role)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    if keyword:
        kw = f"%{keyword}%"
        from sqlalchemy import or_
        stmt = stmt.where(
            or_(User.name.ilike(kw), User.phone.ilike(kw))
        )
    result = await db.execute(stmt.order_by(User.created_at.desc()))
    users = result.scalars().all()
    return ResponseModel(data=[UserOut.model_validate(u) for u in users])


@router.post("", response_model=ResponseModel)
async def create_user(body: UserCreate, db: DBDep, current_user: CurrentUser):
    # 管理员不能添加系统管理员
    if current_user.role == 'admin' and body.role == 'system_admin':
        raise HTTPException(status_code=403, detail='管理员无权创建系统管理员账户')
    if body.role == 'system_admin' and current_user.role != 'system_admin':
        raise HTTPException(status_code=403, detail='无权创建系统管理员账户')
    # Uniqueness checks
    # 检查手机号唯一性
    if body.phone:
        exist = await db.execute(select(User).where(User.phone == body.phone))
        if exist.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="手机号已存在")

    password = _gen_password()
    user = User(
        name=body.name,
        phone=body.phone,
        password_hash=hash_password(password),
        role=body.role,
        must_change_password=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    data = UserCreateResponse.model_validate(user)
    data.generated_password = password
    return ResponseModel(data=data)


@router.put("/{user_id}", response_model=ResponseModel)
async def update_user(user_id: int, body: UserUpdate, db: DBDep):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    for field, value in body.model_dump(exclude_none=True).items():
        if field == "phone":
            continue  # 禁止修改手机号
        setattr(user, field, value)
    await db.commit()
    return ResponseModel(data=UserOut.model_validate(user))


@router.patch("/{user_id}/status", response_model=ResponseModel)
async def toggle_user_status(user_id: int, db: DBDep):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = not user.is_active
    await db.commit()
    return ResponseModel(data=UserOut.model_validate(user))


@router.post("/{user_id}/reset-password", response_model=ResponseModel)
async def reset_password(user_id: int, db: DBDep):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    password = _gen_password()
    user.password_hash = hash_password(password)
    user.must_change_password = True
    await db.commit()
    return ResponseModel(data=ResetPasswordResponse(generated_password=password))
