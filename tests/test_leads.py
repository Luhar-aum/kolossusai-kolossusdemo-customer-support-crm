"""Tests for lead management."""
import pytest
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-123"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
os.environ["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"

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

async def _setup():
    """Helper: register user and return (client, org_id, token)."""
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    reg = await client.post("/api/v1/auth/register", json={
        "email": "user@test.com", "password": "pass123", "full_name": "Test User", "org_name": "Test Org"
    })
    token = reg.json()["access_token"]
    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    org_id = me.json()["organizations"][0]["id"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client, org_id

async def test_create_lead():
    client, org_id = await _setup()
    async with client:
        res = await client.post("/api/v1/leads", json={
            "name": "John Doe", "email": "john@acme.com", "company": "Acme",
            "organization_id": org_id
        })
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "John Doe"
        assert data["status"] == "new"

async def test_duplicate_email_rejected():
    client, org_id = await _setup()
    async with client:
        payload = {"name": "Lead1", "email": "dup@test.com", "organization_id": org_id}
        await client.post("/api/v1/leads", json=payload)
        res = await client.post("/api/v1/leads", json=payload)
        assert res.status_code == 409

async def test_list_leads_pagination():
    client, org_id = await _setup()
    async with client:
        for i in range(5):
            await client.post("/api/v1/leads", json={"name": f"Lead{i}", "organization_id": org_id})
        res = await client.get("/api/v1/leads", params={"organization_id": org_id, "page_size": 3})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 5
        assert len(data["data"]) == 3

async def test_update_lead():
    client, org_id = await _setup()
    async with client:
        create = await client.post("/api/v1/leads", json={"name": "Lead", "organization_id": org_id})
        lead_id = create.json()["id"]
        update = await client.patch(f"/api/v1/leads/{lead_id}", json={"status": "contacted"})
        assert update.status_code == 200
        assert update.json()["status"] == "contacted"

async def test_soft_delete():
    client, org_id = await _setup()
    async with client:
        create = await client.post("/api/v1/leads", json={"name": "ToDelete", "organization_id": org_id})
        lead_id = create.json()["id"]
        del_res = await client.delete(f"/api/v1/leads/{lead_id}")
        assert del_res.status_code == 200
        get_res = await client.get(f"/api/v1/leads/{lead_id}")
        assert get_res.status_code == 404

async def test_search_leads():
    client, org_id = await _setup()
    async with client:
        await client.post("/api/v1/leads", json={"name": "Alice Smith", "email": "alice@acme.com", "organization_id": org_id})
        await client.post("/api/v1/leads", json={"name": "Bob Jones", "organization_id": org_id})
        res = await client.get("/api/v1/leads", params={"organization_id": org_id, "search": "Alice"})
        assert res.json()["total"] == 1
