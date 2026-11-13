"""Tests for lead management."""
import pytest
import os

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
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

async def override_get_db():
    async with TestSession() as s:
        yield s

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def auth_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        reg = await ac.post("/api/v1/auth/register", json={
            "email": "user@test.com", "password": "pass123", "full_name": "Test User", "org_name": "Test Org"
        })
        token = reg.json()["access_token"]
        me = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        org_id = me.json()["organizations"][0]["id"]
        ac.headers.update({"Authorization": f"Bearer {token}"})
        ac.org_id = org_id  # type: ignore
        yield ac

async def test_create_lead(auth_client):
    res = await auth_client.post("/api/v1/leads", json={
        "name": "John Doe", "email": "john@acme.com", "company": "Acme",
        "organization_id": auth_client.org_id  # type: ignore
    })
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "John Doe"
    assert data["status"] == "new"

async def test_duplicate_email_rejected(auth_client):
    payload = {"name": "Lead1", "email": "dup@test.com", "organization_id": auth_client.org_id}  # type: ignore
    await auth_client.post("/api/v1/leads", json=payload)
    res = await auth_client.post("/api/v1/leads", json=payload)
    assert res.status_code == 409

async def test_list_leads_pagination(auth_client):
    for i in range(5):
        await auth_client.post("/api/v1/leads", json={"name": f"Lead{i}", "organization_id": auth_client.org_id})  # type: ignore
    res = await auth_client.get("/api/v1/leads", params={"organization_id": auth_client.org_id, "page_size": 3})  # type: ignore
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 5
    assert len(data["data"]) == 3

async def test_update_lead(auth_client):
    create = await auth_client.post("/api/v1/leads", json={"name": "Lead", "organization_id": auth_client.org_id})  # type: ignore
    lead_id = create.json()["id"]
    update = await auth_client.patch(f"/api/v1/leads/{lead_id}", json={"status": "contacted", "company": "Updated Co"})
    assert update.status_code == 200
    assert update.json()["status"] == "contacted"

async def test_soft_delete(auth_client):
    create = await auth_client.post("/api/v1/leads", json={"name": "ToDelete", "organization_id": auth_client.org_id})  # type: ignore
    lead_id = create.json()["id"]
    del_res = await auth_client.delete(f"/api/v1/leads/{lead_id}")
    assert del_res.status_code == 200
    get_res = await auth_client.get(f"/api/v1/leads/{lead_id}")
    assert get_res.status_code == 404

async def test_search_leads(auth_client):
    await auth_client.post("/api/v1/leads", json={"name": "Alice Smith", "email": "alice@acme.com", "organization_id": auth_client.org_id})  # type: ignore
    await auth_client.post("/api/v1/leads", json={"name": "Bob Jones", "organization_id": auth_client.org_id})  # type: ignore
    res = await auth_client.get("/api/v1/leads", params={"organization_id": auth_client.org_id, "search": "Alice"})  # type: ignore
    assert res.json()["total"] == 1
