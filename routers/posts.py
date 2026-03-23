from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from fastapi import FastAPI, Depends, HTTPException
import models
from database import db_dependency

router = APIRouter()

class PostsRequest(BaseModel):
    title: str
    content: Optional[str] = Field(min_length=1, max_length=256, default=None)
    published: Optional[bool] = Field(default=True)

