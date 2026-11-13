from sqlalchemy import String, Integer, Float, ForeignKey, Enum as SAEnum, Text, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
import enum
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin
from datetime import datetime

class DealStage(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    demo_scheduled = "demo_scheduled"
    proposal_sent = "proposal_sent"
    negotiation = "negotiation"
    won = "won"
    lost = "lost"

class Deal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "deals"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    company_id: Mapped[Optional[str]] = mapped_column(ForeignKey("companies.id"), nullable=True)
    contact_id: Mapped[Optional[str]] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    lead_id: Mapped[Optional[str]] = mapped_column(ForeignKey("leads.id"), nullable=True)
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    probability: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expected_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    stage: Mapped[DealStage] = mapped_column(SAEnum(DealStage), default=DealStage.new, index=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    products: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lost_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
