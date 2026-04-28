from decimal import Decimal
from sqlalchemy import (
    String, Text, SmallInteger, Date, DateTime, Numeric, ForeignKey, func,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class CustomerOrder(Base):
    """PRD订单实体 — 客户预订记录，是业务链的核心锚点。

    与供应商子订单(itinerary.py中的Order)是两个独立概念：
    - CustomerOrder: 客户→旅行社的预订记录
    - Order: 行程内旅行社→供应商的服务采购记录
    """
    __tablename__ = "customer_orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 订单号，服务端生成：ORD-YYYYMM-NNNNNN
    order_no: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # 关联产品（可选，SET NULL on delete）
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # 客户信息
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # 行程信息
    travel_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    days: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    people_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    # 财务信息
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    deposit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    # 关联供应商（可选，SET NULL on delete）
    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True
    )
    supplier_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    profit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    # pending_deposit / pending_payment / completed
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending_deposit")

    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
