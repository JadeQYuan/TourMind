from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_number: Mapped[str] = mapped_column(String(6), unique=True, nullable=False, comment="工号，6位数字，唯一且不可编辑")
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    # employee_id 字段移除，统一用 job_number
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # system_admin / admin / assistant
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="assistant")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
