import os
from typing import Annotated, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from models import Posts
from contextlib import asynccontextmanager
from database import SessionLocal, engine, Base, init_db, get_db
from routers import posts
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

base_dir = os.path.dirname(os.path.abspath(__file__))
favicon_path = os.path.join(base_dir, "static", "favicon.ico")

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

app.include_router(posts.router)


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