from sqlalchemy import String, ForeignKey, Text, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, List
import enum
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

class ConversationChannel(str, enum.Enum):
    email = "email"
    chat = "chat"
    form = "form"
    webhook = "webhook"
    internal = "internal"

class ConversationStatus(str, enum.Enum):
    open = "open"
    pending = "pending"
    resolved = "resolved"
    closed = "closed"

class MessageSentiment(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

class Conversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversations"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    lead_id: Mapped[Optional[str]] = mapped_column(ForeignKey("leads.id"), nullable=True)
    contact_id: Mapped[Optional[str]] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    channel: Mapped[str] = mapped_column(String(50), default="email")
    status: Mapped[str] = mapped_column(String(50), default="open")
    assigned_to: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation")

class Message(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    sender_type: Mapped[str] = mapped_column(String(50))
    sender_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sender_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    approved_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
