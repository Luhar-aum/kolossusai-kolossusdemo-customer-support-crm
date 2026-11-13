from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    organization_id: Mapped[Optional[str]] = mapped_column(ForeignKey("organizations.id"), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    changes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
