from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.task import Task, TaskStatus, TaskPriority, Notification
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    organization_id: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    lead_id: Optional[str] = None
    deal_id: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None

def task_to_dict(t: Task) -> dict:
    return {
        "id": t.id, "organization_id": t.organization_id, "title": t.title,
        "description": t.description, "assigned_to": t.assigned_to,
        "lead_id": t.lead_id, "deal_id": t.deal_id, "due_date": t.due_date,
        "priority": t.priority, "status": t.status, "completed_at": t.completed_at,
        "created_at": t.created_at, "updated_at": t.updated_at,
    }

@router.post("")
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = Task(**data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task_to_dict(task)

@router.get("")
async def list_tasks(organization_id: str, status: Optional[str] = None, assigned_to: Optional[str] = None, page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = select(Task).where(Task.organization_id == organization_id, Task.is_deleted == False)
    if status:
        q = q.where(Task.status == status)
    if assigned_to:
        q = q.where(Task.assigned_to == assigned_to)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar()
    result = await db.execute(q.offset((page-1)*page_size).limit(page_size).order_by(Task.due_date))
    return {"data": [task_to_dict(t) for t in result.scalars().all()], "total": total}

@router.patch("/{task_id}")
async def update_task(task_id: str, data: TaskUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.is_deleted == False))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    if data.status == TaskStatus.completed:
        task.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task_to_dict(task)

@router.delete("/{task_id}")
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    task.is_deleted = True
    await db.commit()
    return {"success": True}

@router.get("/notifications")
async def list_notifications(organization_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(Notification.user_id == current_user.id, Notification.organization_id == organization_id).order_by(Notification.created_at.desc()).limit(50))
    notifs = result.scalars().all()
    return [{"id": n.id, "title": n.title, "body": n.body, "type": n.type, "is_read": n.is_read, "link": n.link, "created_at": n.created_at} for n in notifs]

@router.post("/notifications/{notif_id}/read")
async def mark_read(notif_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id))
    notif = result.scalar_one_or_none()
    if notif:
        notif.is_read = True
        await db.commit()
    return {"success": True}
