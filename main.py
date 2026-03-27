import os
from typing import Annotated, Optional
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from models import Posts
from contextlib import asynccontextmanager
from database import SessionLocal, engine, Base, init_db, get_db
from routers import posts, auth
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

base_dir = os.path.dirname(os.path.abspath(__file__))
favicon_path = os.path.join(base_dir, "static", "favicon.ico")


def parse_csv_env(name: str, default: str) -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def parse_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name, str(default)).strip().lower()
    return raw_value in {"1", "true", "yes", "on"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="AJK Docs",
    description="Anthony's API Documentation",
    version="1.0.1",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    )

# -----Configs-----
default_cors_origins = ",".join(
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.229:5173",
        "http://localhost",
        "http://127.0.0.1",
        "http://192.168.1.229",
        "https://localhost",
        "https://192.168.1.229",
        "https://anthonysjhenry.vercel.app",
    ]
)
default_allowed_hosts = ",".join(
    [
        "localhost",
        "127.0.0.1",
        "192.168.1.229",
        "ajk-backend.onrender.com",
        "*.onrender.com",
    ]
)
origins = parse_csv_env("CORS_ALLOW_ORIGINS", default_cors_origins)
origin_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX", r"https://.*\.vercel\.app")
allow_credentials = parse_bool_env("CORS_ALLOW_CREDENTIALS", False)
allowed_hosts = parse_csv_env("ALLOWED_HOSTS", default_allowed_hosts)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=origin_regex,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)
# -----End of Configs-----

app.include_router(posts.router)
app.include_router(auth.router)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str = "general"):
        await websocket.accept()
        self.active_connections.setdefault(room, []).append(websocket)

    def disconnect(self, websocket: WebSocket, room: str = "general"):
        self.active_connections.get(room, []).remove(websocket)
        if not self.active_connections.get(room):
            self.active_connections.pop(room, None)

    async def broadcast(self, message: str, room: str = "general"):
        for connection in self.active_connections.get(room, []):
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, room)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast(f"A user left the room.", room)

@app.get("/healthy", include_in_schema=False)
async def healthy():
    return {
        "status": "healthy",
        "message": "api is healthy and running"
            }

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        title=app.title,
        openapi_url=app.openapi_url,
        swagger_favicon_url="/favicon.ico"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title,
        redoc_favicon_url="/favicon.ico"
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)
