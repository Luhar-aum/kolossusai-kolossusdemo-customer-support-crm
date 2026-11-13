from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.audit import log_event
from app.models.conversation import Conversation, Message, ConversationChannel, ConversationStatus
from app.models.user import User

router = APIRouter(prefix="/conversations", tags=["conversations"])

class ConversationCreate(BaseModel):
    organization_id: str
    subject: Optional[str] = None
    channel: ConversationChannel = ConversationChannel.email
    lead_id: Optional[str] = None
    contact_id: Optional[str] = None

class MessageCreate(BaseModel):
    body: str
    sender_type: str = "user"
    is_ai_generated: bool = False

def conv_to_dict(c: Conversation) -> dict:
    return {
        "id": c.id, "organization_id": c.organization_id, "subject": c.subject,
        "channel": c.channel, "status": c.status, "assigned_to": c.assigned_to,
        "ai_summary": c.ai_summary, "sentiment": c.sentiment, "priority": c.priority,
        "tags": c.tags, "lead_id": c.lead_id, "contact_id": c.contact_id,
        "created_at": c.created_at, "updated_at": c.updated_at,
    }

def msg_to_dict(m: Message) -> dict:
    return {
        "id": m.id, "conversation_id": m.conversation_id, "body": m.body,
        "sender_type": m.sender_type, "sender_id": m.sender_id, "sender_name": m.sender_name,
        "is_ai_generated": m.is_ai_generated, "is_approved": m.is_approved,
        "is_sent": m.is_sent, "sentiment": m.sentiment, "created_at": m.created_at,
    }

@router.post("")
async def create_conversation(data: ConversationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    conv = Conversation(**data.model_dump(), assigned_to=current_user.id)
    db.add(conv)
    await db.flush()
    await db.commit()
    await db.refresh(conv)
    return conv_to_dict(conv)

@router.get("")
async def list_conversations(organization_id: str, status: Optional[str] = None, page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = select(Conversation).where(Conversation.organization_id == organization_id, Conversation.is_deleted == False)
    if status:
        q = q.where(Conversation.status == status)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    result = await db.execute(q.offset((page-1)*page_size).limit(page_size).order_by(Conversation.created_at.desc()))
    return {"data": [conv_to_dict(c) for c in result.scalars().all()], "total": total}

@router.get("/{conv_id}")
async def get_conversation(conv_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return conv_to_dict(conv)

@router.get("/{conv_id}/messages")
async def list_messages(conv_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Message).where(Message.conversation_id == conv_id).order_by(Message.created_at))
    return [msg_to_dict(m) for m in result.scalars().all()]

@router.post("/{conv_id}/messages")
async def add_message(conv_id: str, data: MessageCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    msg = Message(
        conversation_id=conv_id,
        organization_id=conv.organization_id,
        body=data.body,
        sender_type=data.sender_type,
        sender_id=current_user.id,
        sender_name=current_user.full_name,
        is_ai_generated=data.is_ai_generated,
        is_approved=not data.is_ai_generated,
        is_sent=not data.is_ai_generated,
    )
    db.add(msg)
    if data.is_ai_generated:
        await log_event(db, "ai_message_generated", organization_id=conv.organization_id, user_id=current_user.id, resource_type="message")
    await db.commit()
    await db.refresh(msg)
    return msg_to_dict(msg)

@router.post("/{conv_id}/messages/{msg_id}/approve")
async def approve_message(conv_id: str, msg_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Message).where(Message.id == msg_id, Message.conversation_id == conv_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Message not found")
    msg.is_approved = True
    msg.is_sent = True
    msg.approved_by = current_user.id
    await log_event(db, "message_approved", user_id=current_user.id, resource_type="message", resource_id=msg_id)
    await db.commit()
    return msg_to_dict(msg)
