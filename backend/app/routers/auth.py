from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, or_
from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.core.deps import DBDep, CurrentUser
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, ChangePasswordRequest, UserOut, LoginUserInfo
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/auth", tags=["认证"])

# 简单的登录失败计数（生产环境可用 Redis，此处用内存 dict 满足 ≤20 并发）
_fail_count: dict[str, tuple[int, datetime]] = {}
_MAX_FAILS = 5
_LOCK_MINUTES = 30


def _check_lock(account: str) -> None:
    entry = _fail_count.get(account)
    if entry and entry[0] >= _MAX_FAILS:
        elapsed = (datetime.now(timezone.utc) - entry[1]).total_seconds() / 60
        if elapsed < _LOCK_MINUTES:
            remaining = int(_LOCK_MINUTES - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"账号已锁定，请 {remaining} 分钟后重试",
            )
        else:
            _fail_count.pop(account, None)


def _record_fail(account: str) -> None:
    entry = _fail_count.get(account)
    count = (entry[0] if entry else 0) + 1
    _fail_count[account] = (count, datetime.now(timezone.utc))


def _clear_fail(account: str) -> None:
    _fail_count.pop(account, None)


@router.post("/login", response_model=ResponseModel)
async def login(body: LoginRequest, db: DBDep):
    _check_lock(body.username)

    # 仅支持手机号登录
    result = await db.execute(
        select(User).where(User.phone == body.username)
    )
    user = result.scalar_one_or_none()

    if not user or user.password != body.password:
        _record_fail(body.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已禁用")

    _clear_fail(body.username)
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(user.id, remember_me=body.remember_me)
    return ResponseModel(
        data=TokenResponse(
            access_token=token,
            user=LoginUserInfo(
                id=user.id,
                full_name=user.full_name,
                role=user.role,
                must_change_password=user.must_change_password,
            ),
        )
    )


@router.get("/me", response_model=ResponseModel)
async def get_me(user: CurrentUser):
    return ResponseModel(data=UserOut.model_validate(user))


@router.post("/logout", status_code=204)
async def logout(_: CurrentUser):
    """JWT is stateless; client clears the token. Server just validates and no-ops."""
    return None


@router.post("/change-password", response_model=ResponseModel)
async def change_password(body: ChangePasswordRequest, user: CurrentUser, db: DBDep):
    if user.password != body.old_password:
        raise HTTPException(status_code=400, detail="当前密码错误")

    user.password = body.new_password
    user.must_change_password = False
    await db.commit()
    return ResponseModel(message="密码修改成功")
