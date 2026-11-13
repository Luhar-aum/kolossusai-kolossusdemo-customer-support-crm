from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.audit import log_event
from app.models.lead import Lead, LeadStatus, LeadSource, LeadPriority
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/leads", tags=["leads"])

class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    source: LeadSource = LeadSource.manual
    priority: LeadPriority = LeadPriority.medium
    notes: Optional[str] = None
    organization_id: str

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    status: Optional[LeadStatus] = None
    priority: Optional[LeadPriority] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    lead_score: Optional[int] = None
    next_followup_at: Optional[datetime] = None

def lead_to_dict(lead: Lead) -> dict:
    return {
        "id": lead.id, "name": lead.name, "email": lead.email, "phone": lead.phone,
        "company": lead.company, "job_title": lead.job_title, "industry": lead.industry,
        "country": lead.country, "source": lead.source, "status": lead.status,
        "priority": lead.priority, "lead_score": lead.lead_score,
        "classification": lead.classification, "assigned_to": lead.assigned_to,
        "notes": lead.notes, "last_activity_at": lead.last_activity_at,
        "next_followup_at": lead.next_followup_at, "created_at": lead.created_at,
        "updated_at": lead.updated_at, "organization_id": lead.organization_id,
    }

@router.post("")
async def create_lead(data: LeadCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.email:
        dup = await db.execute(select(Lead).where(Lead.organization_id == data.organization_id, Lead.email == data.email, Lead.is_deleted == False))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Lead with this email already exists")
    lead = Lead(**data.model_dump(), last_activity_at=datetime.utcnow())
    db.add(lead)
    await db.flush()
    await log_event(db, "lead_created", organization_id=data.organization_id, user_id=current_user.id, resource_type="lead", resource_id=lead.id)
    await db.commit()
    await db.refresh(lead)
    return lead_to_dict(lead)

@router.get("")
async def list_leads(
    organization_id: str,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = select(Lead).where(Lead.organization_id == organization_id, Lead.is_deleted == False)
    if status:
        q = q.where(Lead.status == status)
    if search:
        q = q.where(or_(Lead.name.ilike(f"%{search}%"), Lead.email.ilike(f"%{search}%"), Lead.company.ilike(f"%{search}%")))
    total_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(total_q)).scalar()
    q = q.offset((page - 1) * page_size).limit(page_size).order_by(Lead.created_at.desc())
    result = await db.execute(q)
    leads = result.scalars().all()
    return {"data": [lead_to_dict(l) for l in leads], "total": total, "page": page, "page_size": page_size}

@router.get("/{lead_id}")
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.is_deleted == False))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead_to_dict(lead)

@router.patch("/{lead_id}")
async def update_lead(lead_id: str, data: LeadUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.is_deleted == False))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(lead, field, value)
    lead.last_activity_at = datetime.utcnow()
    await log_event(db, "lead_updated", organization_id=lead.organization_id, user_id=current_user.id, resource_type="lead", resource_id=lead_id)
    await db.commit()
    await db.refresh(lead)
    return lead_to_dict(lead)

@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.is_deleted == False))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.is_deleted = True
    await log_event(db, "lead_deleted", organization_id=lead.organization_id, user_id=current_user.id, resource_type="lead", resource_id=lead_id)
    await db.commit()
    return {"success": True}
