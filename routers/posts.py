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

@router.get("/")
async def read_all(db: db_dependency):
    result = await db.execute(select(models.Posts))
    return result.scalars().all()

@router.post("/posts")
async def create_post(post: PostsRequest, db: db_dependency):
    new_post = models.Posts(**post.dict())
    print(new_post)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return await read_all(db)


