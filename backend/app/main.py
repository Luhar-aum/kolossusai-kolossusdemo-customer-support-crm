from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, leads, deals, conversations, tasks, ai, analytics, workflows, integrations
import app.models  # ensure all models are registered
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CRM API...")
    yield
    logger.info("Shutting down CRM API...")
    await engine.dispose()

app = FastAPI(
    title="Customer Support CRM API",
    description="AI-powered Sales and Customer Support CRM",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(leads.router, prefix="/api/v1")
app.include_router(deals.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, org_id: str):
        await websocket.accept()
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        self.active_connections[org_id].append(websocket)

    def disconnect(self, websocket: WebSocket, org_id: str):
        if org_id in self.active_connections:
            self.active_connections[org_id].remove(websocket)

    async def broadcast(self, message: dict, org_id: str):
        import json
        if org_id in self.active_connections:
            for ws in self.active_connections[org_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()

@app.websocket("/ws/{org_id}")
async def websocket_endpoint(websocket: WebSocket, org_id: str):
    await manager.connect(websocket, org_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast({"type": "message", "data": data}, org_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, org_id)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "Customer Support CRM API", "docs": "/docs"}
