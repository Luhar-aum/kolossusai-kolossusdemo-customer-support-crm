from sqlalchemy import String, ForeignKey, Enum as SAEnum, Text, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from typing import Optional
import enum
from datetime import datetime
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    blocked = "blocked"
    completed = "completed"
    cancelled = "cancelled"

class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tasks"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    lead_id: Mapped[Optional[str]] = mapped_column(ForeignKey("leads.id"), nullable=True)
    deal_id: Mapped[Optional[str]] = mapped_column(ForeignKey("deals.id"), nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(SAEnum(TaskPriority), default=TaskPriority.medium)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), default=TaskStatus.todo, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)

class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), default="info")
    is_read: Mapped[bool] = mapped_column(default=False)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    related_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    related_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
