from sqlalchemy import String, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, List
import enum
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

class UserRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    manager = "manager"
    sales_rep = "sales_rep"
    support_rep = "support_rep"
    read_only = "read_only"

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    memberships: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="user")
