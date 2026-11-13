from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.audit import log_event
from app.models.deal import Deal, DealStage
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/deals", tags=["deals"])

class DealCreate(BaseModel):
    name: str
    organization_id: str
    company_id: Optional[str] = None
    contact_id: Optional[str] = None
    lead_id: Optional[str] = None
    value: Optional[float] = None
    currency: str = "USD"
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None
    stage: DealStage = DealStage.new
    products: Optional[str] = None
    notes: Optional[str] = None

class DealUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[float] = None
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None
    stage: Optional[DealStage] = None
    notes: Optional[str] = None
    lost_reason: Optional[str] = None
    assigned_to: Optional[str] = None

def deal_to_dict(d: Deal) -> dict:
    return {
        "id": d.id, "name": d.name, "organization_id": d.organization_id,
        "company_id": d.company_id, "contact_id": d.contact_id, "lead_id": d.lead_id,
        "value": d.value, "currency": d.currency, "probability": d.probability,
        "expected_close_date": d.expected_close_date, "stage": d.stage,
        "assigned_to": d.assigned_to, "products": d.products, "notes": d.notes,
        "lost_reason": d.lost_reason, "created_at": d.created_at, "updated_at": d.updated_at,
    }

@router.post("")
async def create_deal(data: DealCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    deal = Deal(**data.model_dump(), assigned_to=current_user.id)
    db.add(deal)
    await db.flush()
    await log_event(db, "deal_created", organization_id=data.organization_id, user_id=current_user.id, resource_type="deal", resource_id=deal.id)
    await db.commit()
    await db.refresh(deal)
    return deal_to_dict(deal)

@router.get("")
async def list_deals(organization_id: str, stage: Optional[str] = None, page: int = 1, page_size: int = 50, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = select(Deal).where(Deal.organization_id == organization_id, Deal.is_deleted == False)
    if stage:
        q = q.where(Deal.stage == stage)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    result = await db.execute(q.offset((page-1)*page_size).limit(page_size).order_by(Deal.created_at.desc()))
    return {"data": [deal_to_dict(d) for d in result.scalars().all()], "total": total}

@router.get("/{deal_id}")
async def get_deal(deal_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")
    return deal_to_dict(deal)

@router.patch("/{deal_id}")
async def update_deal(deal_id: str, data: DealUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")
    old_stage = deal.stage
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(deal, field, value)
    if data.stage and data.stage != old_stage:
        await log_event(db, "deal_stage_changed", organization_id=deal.organization_id, user_id=current_user.id, resource_type="deal", resource_id=deal_id, description=f"Stage: {old_stage} → {data.stage}")
    await db.commit()
    await db.refresh(deal)
    return deal_to_dict(deal)

@router.delete("/{deal_id}")
async def delete_deal(deal_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")
    deal.is_deleted = True
    await db.commit()
    return {"success": True}

@router.post("/{deal_id}/move-stage")
async def move_stage(deal_id: str, stage: DealStage, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id, Deal.is_deleted == False))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(404, "Deal not found")
    old = deal.stage
    deal.stage = stage
    await log_event(db, "deal_stage_changed", organization_id=deal.organization_id, user_id=current_user.id, resource_type="deal", resource_id=deal_id, description=f"{old} → {stage}")
    await db.commit()
    await db.refresh(deal)
    return deal_to_dict(deal)
