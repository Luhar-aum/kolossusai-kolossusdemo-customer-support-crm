from sqlalchemy import String, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, List
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin
from app.models.user import UserRole

class Organization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    members: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="organization")

class OrganizationMember(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organization_members"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.sales_rep)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    invited_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships", foreign_keys="[OrganizationMember.user_id]")
