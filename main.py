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
from fastapi.openapi.docs import get_swagger_ui_html

base_dir = os.path.dirname(os.path.abspath(__file__))
favicon_path = os.path.join(base_dir, "favicon.ico")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    lifespan=lifespan,
    docs_url=None
    )