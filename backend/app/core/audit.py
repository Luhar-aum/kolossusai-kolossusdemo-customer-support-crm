from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from typing import Optional

async def log_event(
    db: AsyncSession,
    event_type: str,
    organization_id: Optional[str] = None,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    changes: Optional[str] = None,
):
    log = AuditLog(
        event_type=event_type,
        organization_id=organization_id,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=ip_address,
        changes=changes,
    )
    db.add(log)
    await db.flush()
