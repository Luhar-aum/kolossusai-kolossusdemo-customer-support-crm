from sqlalchemy import String, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, List
import enum
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

class WorkflowStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    draft = "draft"
    archived = "archived"

class ExecutionStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    paused = "paused"

class Workflow(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflows"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(100))
    trigger_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))

    steps: Mapped[List["WorkflowStep"]] = relationship("WorkflowStep", back_populates="workflow", order_by="WorkflowStep.order")
    executions: Mapped[List["WorkflowExecution"]] = relationship("WorkflowExecution", back_populates="workflow")

class WorkflowStep(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflow_steps"

    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    action_type: Mapped[str] = mapped_column(String(100))
    action_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)

    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="steps")

class WorkflowExecution(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflow_executions"

    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), index=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    trigger_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="executions")
