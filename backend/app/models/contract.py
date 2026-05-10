from sqlalchemy import (
    String, Text, SmallInteger, Date, DateTime, Numeric,
    ForeignKey, func, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )
    source_itinerary_id: Mapped[int | None] = mapped_column(
        ForeignKey("itineraries.id", ondelete="SET NULL"), nullable=True
    )

    # 客户信息（从行程复制，合同内独立保存）
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    # 甲乙方及联系电话
    party_a: Mapped[str | None] = mapped_column(String(100), nullable=True)
    party_a_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    party_b: Mapped[str | None] = mapped_column(String(100), nullable=True)
    party_b_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pax: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    travelers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # 行程时间
    departure_date: Mapped[Date] = mapped_column(Date, nullable=False)
    return_date: Mapped[Date] = mapped_column(Date, nullable=False)

    # 费用条款
    total_amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)
    price_per_person: Mapped[Numeric | None] = mapped_column(Numeric(10, 2), nullable=True)
    deposit_amount: Mapped[Numeric | None] = mapped_column(Numeric(10, 2), nullable=True)
    deposit_due_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    balance_amount: Mapped[Numeric | None] = mapped_column(Numeric(10, 2), nullable=True)
    balance_due_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    includes: Mapped[str | None] = mapped_column(Text, nullable=True)
    excludes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    travel_notice: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 状态
    # pending_sign / signed / revoked
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending_sign")
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 客户签署相关
    share_token: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    signed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signature_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # [{name, id_type, id_no, front_url, back_url}]
    id_documents: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    days_detail: Mapped[list["ContractDay"]] = relationship(
        "ContractDay", back_populates="contract", cascade="all, delete-orphan",
        order_by="ContractDay.day_number",
    )


class ContractDay(Base):
    __tablename__ = "contract_days"
    __table_args__ = (UniqueConstraint("contract_id", "day_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False
    )
    day_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False, default="")
    accommodation_area: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="days_detail")
