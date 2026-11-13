import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UUIDMixin:
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
