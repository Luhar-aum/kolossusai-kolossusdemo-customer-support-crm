from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.audit import log_event
from app.models.lead import Lead, AIRecommendation
from app.models.user import User
from app.services.ai_service import qualify_lead, suggest_reply, summarize_conversation
import json

router = APIRouter(prefix="/ai", tags=["ai"])

class OverrideRequest(BaseModel):
    score: int
    reason: str

@router.post("/leads/{lead_id}/qualify")
async def qualify_lead_endpoint(lead_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.is_deleted == False))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")
    
    ai_result = await qualify_lead(lead)
    
    rec = AIRecommendation(
        organization_id=lead.organization_id,
        lead_id=lead.id,
        score=ai_result.get("score"),
        classification=ai_result.get("classification"),
        intent=ai_result.get("intent"),
        reasoning=json.dumps(ai_result.get("reasoning", [])),
        recommended_action=ai_result.get("recommended_action"),
        confidence=ai_result.get("confidence"),
        model_name=ai_result.get("model_name", "mock"),
        prompt_version="v1",
    )
    db.add(rec)
    lead.lead_score = ai_result.get("score")
    lead.classification = ai_result.get("classification")
    
    await log_event(db, "ai_recommendation", organization_id=lead.organization_id, user_id=current_user.id, resource_type="lead", resource_id=lead_id)
    await db.commit()
    await db.refresh(rec)
    return {
        "recommendation_id": rec.id,
        "score": rec.score,
        "classification": rec.classification,
        "intent": rec.intent,
        "reasoning": json.loads(rec.reasoning) if rec.reasoning else [],
        "recommended_action": rec.recommended_action,
        "confidence": rec.confidence,
        "model_name": rec.model_name,
        "is_ai_generated": True,
    }

@router.post("/leads/{lead_id}/override-score")
async def override_score(lead_id: str, data: OverrideRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")
    lead.lead_score = data.score
    result2 = await db.execute(select(AIRecommendation).where(AIRecommendation.lead_id == lead_id).order_by(AIRecommendation.created_at.desc()))
    rec = result2.scalars().first()
    if rec:
        rec.is_overridden = True
        rec.override_reason = data.reason
    await db.commit()
    return {"success": True, "new_score": data.score}

@router.post("/conversations/{conv_id}/suggest-reply")
async def suggest_reply_endpoint(conv_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.conversation import Conversation, Message
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    result2 = await db.execute(select(Message).where(Message.conversation_id == conv_id).order_by(Message.created_at).limit(10))
    messages = result2.scalars().all()
    suggestion = await suggest_reply(conv, messages)
    return {"suggested_reply": suggestion, "is_ai_generated": True, "requires_approval": True}

@router.post("/conversations/{conv_id}/summarize")
async def summarize_conv(conv_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.conversation import Conversation, Message
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    result2 = await db.execute(select(Message).where(Message.conversation_id == conv_id).order_by(Message.created_at))
    messages = result2.scalars().all()
    summary = await summarize_conversation(messages)
    conv.ai_summary = summary
    await db.commit()
    return {"summary": summary, "is_ai_generated": True}
