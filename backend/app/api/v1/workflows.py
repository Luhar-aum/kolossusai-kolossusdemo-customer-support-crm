from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.workflow import Workflow, WorkflowStep, WorkflowExecution, WorkflowStatus
from app.models.user import User
import json

router = APIRouter(prefix="/workflows", tags=["workflows"])

class StepCreate(BaseModel):
    name: str
    action_type: str
    action_config: Optional[dict] = None
    conditions: Optional[dict] = None
    order: int = 0
    requires_approval: bool = False

class WorkflowCreate(BaseModel):
    organization_id: str
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: Optional[dict] = None
    steps: List[StepCreate] = []

def wf_to_dict(w: Workflow) -> dict:
    return {"id": w.id, "name": w.name, "description": w.description, "trigger_type": w.trigger_type, "status": w.status, "organization_id": w.organization_id, "created_at": w.created_at}

@router.post("")
async def create_workflow(data: WorkflowCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    wf = Workflow(
        organization_id=data.organization_id, name=data.name, description=data.description,
        trigger_type=data.trigger_type,
        trigger_config=json.dumps(data.trigger_config) if data.trigger_config else None,
        created_by=current_user.id,
    )
    db.add(wf)
    await db.flush()
    for step_data in data.steps:
        step = WorkflowStep(
            workflow_id=wf.id, name=step_data.name, action_type=step_data.action_type,
            action_config=json.dumps(step_data.action_config) if step_data.action_config else None,
            conditions=json.dumps(step_data.conditions) if step_data.conditions else None,
            order=step_data.order, requires_approval=step_data.requires_approval,
        )
        db.add(step)
    await db.commit()
    await db.refresh(wf)
    return wf_to_dict(wf)

@router.get("")
async def list_workflows(organization_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Workflow).where(Workflow.organization_id == organization_id).order_by(Workflow.created_at.desc()))
    return [wf_to_dict(w) for w in result.scalars().all()]

@router.patch("/{wf_id}/status")
async def update_workflow_status(wf_id: str, status: WorkflowStatus, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Workflow).where(Workflow.id == wf_id))
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(404, "Workflow not found")
    wf.status = status
    await db.commit()
    return wf_to_dict(wf)

@router.get("/{wf_id}/executions")
async def list_executions(wf_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(WorkflowExecution).where(WorkflowExecution.workflow_id == wf_id).order_by(WorkflowExecution.created_at.desc()).limit(50))
    execs = result.scalars().all()
    return [{"id": e.id, "status": e.status, "execution_log": e.execution_log, "error_message": e.error_message, "created_at": e.created_at} for e in execs]
