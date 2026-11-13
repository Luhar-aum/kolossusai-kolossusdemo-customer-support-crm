from sqlalchemy import String, Integer, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, List
import enum
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin
from datetime import datetime

class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    unqualified = "unqualified"
    converted = "converted"
    lost = "lost"

class LeadSource(str, enum.Enum):
    manual = "manual"
    csv_import = "csv_import"
    public_form = "public_form"
    webhook = "webhook"
    email = "email"
    website = "website"

class LeadPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class LeadClassification(str, enum.Enum):
    hot = "hot"
    warm = "warm"
    cold = "cold"

class Lead(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "leads"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="manual")
    status: Mapped[str] = mapped_column(String(50), default="new", index=True)
    priority: Mapped[str] = mapped_column(String(50), default="medium")
    lead_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    classification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_followup_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    ai_recommendations: Mapped[List["AIRecommendation"]] = relationship("AIRecommendation", back_populates="lead")

class Company(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "companies"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)

class Contact(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contacts"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    company_id: Mapped[Optional[str]] = mapped_column(ForeignKey("companies.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)

class AIRecommendation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_recommendations"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    lead_id: Mapped[Optional[str]] = mapped_column(ForeignKey("leads.id"), nullable=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    classification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_overridden: Mapped[bool] = mapped_column(default=False)
    override_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="ai_recommendations")
