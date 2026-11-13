"""Tests for authentication and organization isolation."""
import pytest
import os
import asyncio

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SYNC_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-123")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

async def test_register_and_login(client):
    res = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "org_name": "Test Org"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["email"] == "test@example.com"

async def test_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "pass123", "full_name": "User", "org_name": "Org"}
    await client.post("/api/v1/auth/register", json=payload)
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 400

async def test_login_invalid_credentials(client):
    res = await client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "wrong"})
    assert res.status_code == 401

async def test_me_requires_auth(client):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 403

async def test_me_with_valid_token(client):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "me@example.com", "password": "pass123", "full_name": "Me", "org_name": "MyOrg"
    })
    token = reg.json()["access_token"]
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"

async def test_lead_org_isolation(client):
    reg1 = await client.post("/api/v1/auth/register", json={"email": "org1@t.com", "password": "p", "full_name": "U1", "org_name": "Org1"})
    reg2 = await client.post("/api/v1/auth/register", json={"email": "org2@t.com", "password": "p", "full_name": "U2", "org_name": "Org2"})
    token1 = reg1.json()["access_token"]
    token2 = reg2.json()["access_token"]

    me1 = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token1}"})
    org1_id = me1.json()["organizations"][0]["id"]

    lead = await client.post("/api/v1/leads", json={
        "name": "Lead Org1", "organization_id": org1_id
    }, headers={"Authorization": f"Bearer {token1}"})
    assert lead.status_code == 200

    me2 = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token2}"})
    org2_id = me2.json()["organizations"][0]["id"]

    leads_org2 = await client.get("/api/v1/leads", params={"organization_id": org2_id}, headers={"Authorization": f"Bearer {token2}"})
    assert leads_org2.status_code == 200
    assert leads_org2.json()["total"] == 0
