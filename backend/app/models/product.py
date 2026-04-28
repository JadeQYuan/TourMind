from sqlalchemy import String, Text, Boolean, SmallInteger, Numeric, DateTime, ForeignKey, func, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # optional: tour_group / independent / custom / semi_independent / other
    product_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    destination: Mapped[str] = mapped_column(String(200), nullable=False)
    days: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reference_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    includes: Mapped[str | None] = mapped_column(Text, nullable=True)
    excludes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    travel_notice: Mapped[str | None] = mapped_column(Text, nullable=True)
    important_tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    # [{seq, details, accommodation_area, notes}]
    itinerary_template: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # active / inactive
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
