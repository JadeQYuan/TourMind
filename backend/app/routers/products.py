from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy import select
from app.core.deps import DBDep, CurrentUser
from app.core.audit import write_log
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut, ProductListItem
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/products", tags=["产品"])


@router.get("", response_model=ResponseModel)
async def list_products(
    db: DBDep,
    _: CurrentUser,
    keyword: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    stmt = select(Product)
    if keyword:
        stmt = stmt.where(Product.name.ilike(f"%{keyword}%"))
    if status:
        stmt = stmt.where(Product.status == status)
    stmt = stmt.order_by(Product.created_at.desc())

    result = await db.execute(stmt)
    items = result.scalars().all()
    return ResponseModel(data=[ProductListItem.model_validate(p) for p in items])


@router.get("/{product_id}", response_model=ResponseModel)
async def get_product(product_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return ResponseModel(data=ProductOut.model_validate(product))


@router.post("", response_model=ResponseModel)
async def create_product(request: Request, body: ProductCreate, db: DBDep, user: CurrentUser):
    product = Product(**body.model_dump(), created_by=user.id)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    # await write_log(db, request, user, "product", product.id, "create", {"name": product.name})
    return ResponseModel(data=ProductOut.model_validate(product))


@router.put("/{product_id}", response_model=ResponseModel)
async def update_product(request: Request, product_id: int, body: ProductUpdate, db: DBDep, user: CurrentUser):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    # await write_log(db, request, user, "product", product_id, "update", {})
    return ResponseModel(data=ProductOut.model_validate(product))


@router.post("/{product_id}/copy", response_model=ResponseModel)
async def copy_product(product_id: int, db: DBDep, user: CurrentUser):
    result = await db.execute(select(Product).where(Product.id == product_id))
    src = result.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=404, detail="产品不存在")
    new_product = Product(
        name=f"{src.name}（复制）",
        origin=src.origin,
        destination=src.destination,
        days=src.days,
        price=src.price,
        includes=src.includes,
        excludes=src.excludes,
        cancellation_policy=src.cancellation_policy,
        travel_notice=src.travel_notice,
        important_tips=src.important_tips,
        itinerary_template=src.itinerary_template,
        remark=src.remark,
        status="disabled",
        created_by=user.id,
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return ResponseModel(data=ProductOut.model_validate(new_product))


@router.patch("/{product_id}/status", response_model=ResponseModel)
async def toggle_product_status(product_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    product.status = "disabled" if product.status == "enabled" else "enabled"
    await db.commit()
    await db.refresh(product)
    return ResponseModel(data=ProductOut.model_validate(product))


@router.delete("/{product_id}", response_model=ResponseModel)
async def delete_product(product_id: int, db: DBDep, _: CurrentUser):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    await db.delete(product)
    await db.commit()
    return ResponseModel(message="删除成功")
