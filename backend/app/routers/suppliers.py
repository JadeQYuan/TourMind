from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy import select
from app.core.deps import DBDep, CurrentUser, require_roles
from app.core.audit import write_log
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierOut
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/suppliers", tags=["供应商"])


@router.get("", response_model=ResponseModel)
async def list_suppliers(
    db: DBDep,
    _: CurrentUser,
    supplier_type: str | None = None,
    is_active: bool | None = None,
):
    stmt = select(Supplier)
    if supplier_type:
        stmt = stmt.where(Supplier.supplier_type == supplier_type)
    if is_active is not None:
        stmt = stmt.where(Supplier.is_active == is_active)
    result = await db.execute(stmt.order_by(Supplier.name))
    return ResponseModel(data=[SupplierOut.model_validate(s) for s in result.scalars().all()])


@router.post("", response_model=ResponseModel)
async def create_supplier(request: Request, body: SupplierCreate, db: DBDep, user: CurrentUser):
    supplier = Supplier(**body.model_dump(), created_by=user.id)
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    await write_log(db, request, user, "supplier", supplier.id, "create", {"name": supplier.name})
    return ResponseModel(data=SupplierOut.model_validate(supplier))


@router.put("/{supplier_id}", response_model=ResponseModel)
async def update_supplier(request: Request, supplier_id: int, body: SupplierUpdate, db: DBDep, user: CurrentUser):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(supplier, field, value)
    await db.commit()
    await write_log(db, request, user, "supplier", supplier_id, "update", {})
    return ResponseModel(data=SupplierOut.model_validate(supplier))


@router.delete("/{supplier_id}", response_model=ResponseModel, dependencies=[Depends(require_roles("admin"))])
async def delete_supplier(supplier_id: int, db: DBDep):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    await db.delete(supplier)
    await db.commit()
    return ResponseModel(message="删除成功")
