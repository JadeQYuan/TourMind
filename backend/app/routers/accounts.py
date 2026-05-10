from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy import select
from app.core.deps import DBDep, CurrentUser, require_roles
from app.core.audit import write_log
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/accounts", tags=["账户"])


async def _resolve_user_names(db, accounts: list) -> list[AccountOut]:
    """Resolve user_name by looking up user_id values in a single query."""
    user_ids = {a.user_id for a in accounts if a.user_id}
    user_map: dict[int, str] = {}
    if user_ids:
        result = await db.execute(select(User).where(User.id.in_(user_ids)))
        user_map = {u.id: u.name for u in result.scalars().all()}

    out = []
    for a in accounts:
        data = AccountOut.model_validate(a)
        data.user_name = user_map.get(a.user_id) if a.user_id else None
        out.append(data)
    return out


@router.get("", response_model=ResponseModel)
async def list_accounts(db: DBDep, _: CurrentUser, status: str | None = None):
    stmt = select(Account)
    if status is not None:
        stmt = stmt.where(Account.status == status)
    result = await db.execute(stmt.order_by(Account.name))
    accounts = result.scalars().all()
    return ResponseModel(data=await _resolve_user_names(db, accounts))


@router.post("", response_model=ResponseModel)
async def create_account(request: Request, body: AccountCreate, db: DBDep, user: CurrentUser):
    account = Account(**body.model_dump(), created_by=user.id)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    await write_log(db, request, user, "account", account.id, "create", {"name": account.name})
    return ResponseModel(data=(await _resolve_user_names(db, [account]))[0])


@router.put("/{account_id}", response_model=ResponseModel)
async def update_account(request: Request, account_id: int, body: AccountUpdate, db: DBDep, user: CurrentUser):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(account, field, value)
    await db.commit()
    await write_log(db, request, user, "account", account_id, "update", {})
    return ResponseModel(data=(await _resolve_user_names(db, [account]))[0])


@router.delete("/{account_id}", response_model=ResponseModel, dependencies=[Depends(require_roles("admin"))])
async def delete_account(account_id: int, db: DBDep):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    await db.delete(account)
    await db.commit()
    return ResponseModel(message="删除成功")
