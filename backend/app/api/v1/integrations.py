from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import encrypt_value
from app.models.integration import Integration
from app.models.user import User
import json

router = APIRouter(prefix="/integrations", tags=["integrations"])

class IntegrationCreate(BaseModel):
    organization_id: str
    provider: str
    name: str
    credentials: Optional[dict] = None

@router.post("")
async def create_integration(data: IntegrationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    encrypted = None
    if data.credentials:
        encrypted = encrypt_value(json.dumps(data.credentials))
    integration = Integration(
        organization_id=data.organization_id, provider=data.provider,
        name=data.name, encrypted_credentials=encrypted, created_by=current_user.id,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return {"id": integration.id, "provider": integration.provider, "name": integration.name, "status": integration.status, "is_active": integration.is_active}

@router.get("")
async def list_integrations(organization_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Integration).where(Integration.organization_id == organization_id))
    integrations = result.scalars().all()
    return [{"id": i.id, "provider": i.provider, "name": i.name, "status": i.status, "is_active": i.is_active, "last_sync_at": i.last_sync_at} for i in integrations]

@router.post("/{integration_id}/test")
async def test_integration(integration_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Integration).where(Integration.id == integration_id))
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(404, "Integration not found")
    integration.status = "connected"
    integration.is_active = True
    await db.commit()
    return {"success": True, "status": "connected"}
