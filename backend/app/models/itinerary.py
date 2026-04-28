from sqlalchemy import (
    String, Text, Boolean, SmallInteger, Date, DateTime,
    Numeric, Integer, ForeignKey, func, ARRAY, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Itinerary(Base):
    __tablename__ = "itineraries"
    __table_args__ = (UniqueConstraint("customer_order_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(200), nullable=False)
    days: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    departure_date: Mapped[Date] = mapped_column(Date, nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
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
    # 1:1 link to CustomerOrder (UNIQUE constraint above)
    customer_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("customer_orders.id", ondelete="SET NULL"), nullable=True
    )

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    days_detail: Mapped[list["ItineraryDay"]] = relationship(
        "ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan",
        order_by="ItineraryDay.day_number",
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="itinerary", cascade="all, delete-orphan",
    )


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"
    __table_args__ = (UniqueConstraint("itinerary_id", "day_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    itinerary_id: Mapped[int] = mapped_column(
        ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False
    )
    day_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False, default="")
    accommodation_area: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="days_detail")
    attachments: Mapped[list["ItineraryAttachment"]] = relationship(
        "ItineraryAttachment", back_populates="day", cascade="all, delete-orphan",
    )


class ItineraryAttachment(Base):
    __tablename__ = "itinerary_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    day_id: Mapped[int] = mapped_column(
        ForeignKey("itinerary_days.id", ondelete="CASCADE"), nullable=False
    )
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    day: Mapped["ItineraryDay"] = relationship("ItineraryDay", back_populates="attachments")


class Order(Base):
    """行程内的供应商订单"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    itinerary_id: Mapped[int] = mapped_column(
        ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False
    )
    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True
    )
    # transport / accommodation / attraction / meal / guide / insurance / other
    service_type: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)
    order_date: Mapped[Date] = mapped_column(Date, nullable=False)
    related_days: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    # pending / confirmed / cancelled
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="orders")
    attachments: Mapped[list["OrderAttachment"]] = relationship(
        "OrderAttachment", back_populates="order", cascade="all, delete-orphan",
    )


class OrderAttachment(Base):
    __tablename__ = "order_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order: Mapped["Order"] = relationship("Order", back_populates="attachments")
