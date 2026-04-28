from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AuditLog(Base):
    """只追加的操作审计记录。仅系统管理员可读，任何接口不允许修改或删除。"""
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_created_at", "created_at"),
        Index("ix_audit_logs_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # 操作者（SET NULL on delete，保留日志完整性）
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    user_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 操作描述，例如 create_order / delete_product / login
    action: Mapped[str] = mapped_column(String(100), nullable=False)

    # 被操作资源
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # 变更详情（JSON格式，记录变更前/后字段值）
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 客户端IP
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
