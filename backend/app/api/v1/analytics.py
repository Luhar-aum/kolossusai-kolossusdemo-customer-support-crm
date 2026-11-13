from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.lead import Lead, LeadStatus
from app.models.deal import Deal, DealStage
from app.models.task import Task, TaskStatus
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def dashboard(organization_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_leads = (await db.execute(select(func.count(Lead.id)).where(Lead.organization_id == organization_id, Lead.is_deleted == False))).scalar()
    qualified_leads = (await db.execute(select(func.count(Lead.id)).where(Lead.organization_id == organization_id, Lead.status == LeadStatus.qualified, Lead.is_deleted == False))).scalar()
    converted_leads = (await db.execute(select(func.count(Lead.id)).where(Lead.organization_id == organization_id, Lead.status == LeadStatus.converted, Lead.is_deleted == False))).scalar()
    pipeline_value = float((await db.execute(select(func.coalesce(func.sum(Deal.value), 0)).where(Deal.organization_id == organization_id, Deal.is_deleted == False, Deal.stage.notin_([DealStage.won, DealStage.lost])))).scalar())
    won_deals = (await db.execute(select(func.count(Deal.id)).where(Deal.organization_id == organization_id, Deal.stage == DealStage.won, Deal.is_deleted == False))).scalar()
    lost_deals = (await db.execute(select(func.count(Deal.id)).where(Deal.organization_id == organization_id, Deal.stage == DealStage.lost, Deal.is_deleted == False))).scalar()
    won_revenue = float((await db.execute(select(func.coalesce(func.sum(Deal.value), 0)).where(Deal.organization_id == organization_id, Deal.stage == DealStage.won, Deal.is_deleted == False))).scalar())
    conversion_rate = round(converted_leads / total_leads * 100, 2) if total_leads > 0 else 0
    stages_result = await db.execute(select(Deal.stage, func.count(Deal.id), func.coalesce(func.sum(Deal.value), 0)).where(Deal.organization_id == organization_id, Deal.is_deleted == False).group_by(Deal.stage))
    stages_data = [{"stage": row[0], "count": row[1], "value": float(row[2])} for row in stages_result.all()]
    lead_status_result = await db.execute(select(Lead.status, func.count(Lead.id)).where(Lead.organization_id == organization_id, Lead.is_deleted == False).group_by(Lead.status))
    lead_status_data = [{"status": row[0], "count": row[1]} for row in lead_status_result.all()]
    return {
        "total_leads": total_leads, "qualified_leads": qualified_leads, "converted_leads": converted_leads,
        "conversion_rate": conversion_rate, "pipeline_value": pipeline_value,
        "won_deals": won_deals, "lost_deals": lost_deals, "won_revenue": won_revenue,
        "deals_by_stage": stages_data, "leads_by_status": lead_status_data,
    }
