from sqlalchemy import (
    String, Text, Boolean, SmallInteger, Date, DateTime,
    Numeric, Integer, ForeignKey, func, ARRAY, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class Itinerary(Base):
    __tablename__ = "itineraries"
    __table_args__ = (UniqueConstraint("order_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(200), nullable=False)
    days: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    departure_date: Mapped[Date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 客户信息
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    pax: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    travelers: Mapped[str | None] = mapped_column(Text, nullable=True)

    # not_started / in_progress / completed
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")

    # share link for public read-only view
    share_token: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)

    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    # 1:1 link to Order (UNIQUE constraint above)
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    details: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True, default=list)
