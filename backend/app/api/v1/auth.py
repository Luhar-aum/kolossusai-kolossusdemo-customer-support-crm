from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.audit import log_event
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    org_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str

@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        is_verified=True,
    )
    db.add(user)
    await db.flush()

    slug = req.org_name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8]
    org = Organization(name=req.org_name, slug=slug)
    db.add(org)
    await db.flush()

    member = OrganizationMember(organization_id=org.id, user_id=user.id, role="owner")
    db.add(member)
    
    await log_event(db, "user_registered", user_id=user.id, description=f"User {user.email} registered")
    await db.commit()

    token = create_access_token({"sub": user.id, "org_id": org.id})
    return TokenResponse(access_token=token, user_id=user.id, email=user.email, full_name=user.full_name)

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account disabled")
    
    result2 = await db.execute(select(OrganizationMember).where(OrganizationMember.user_id == user.id, OrganizationMember.is_active == True))
    member = result2.scalars().first()
    org_id = member.organization_id if member else ""

    await log_event(db, "user_login", user_id=user.id, organization_id=org_id, description=f"User {user.email} logged in", ip_address=request.client.host if request.client else None)
    await db.commit()

    token = create_access_token({"sub": user.id, "org_id": org_id})
    return TokenResponse(access_token=token, user_id=user.id, email=user.email, full_name=user.full_name)

@router.get("/me")
async def me(db: AsyncSession = Depends(get_db), current_user=Depends(__import__('app.core.deps', fromlist=['get_current_user']).get_current_user)):
    result = await db.execute(select(OrganizationMember).where(OrganizationMember.user_id == current_user.id, OrganizationMember.is_active == True))
    members = result.scalars().all()
    orgs = []
    for m in members:
        org_result = await db.execute(select(Organization).where(Organization.id == m.organization_id))
        org = org_result.scalar_one_or_none()
        if org:
            orgs.append({"id": org.id, "name": org.name, "slug": org.slug, "role": m.role})
    return {"id": current_user.id, "email": current_user.email, "full_name": current_user.full_name, "organizations": orgs}
