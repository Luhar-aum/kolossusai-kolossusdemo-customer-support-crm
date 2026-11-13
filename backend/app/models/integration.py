from sqlalchemy import String, ForeignKey, Text, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from typing import Optional
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

class Integration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integrations"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    provider: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    encrypted_credentials: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(50), default="disconnected")
    last_sync_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
