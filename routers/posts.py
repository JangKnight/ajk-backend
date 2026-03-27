from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional
import models
from database import db_dependency
from routers.auth import user_dependency

router = APIRouter()

class PostsRequest(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    content: Optional[str] = Field(default=None, max_length=4000)
    published: Optional[bool] = Field(default=True)


def build_public_blog_statement():
    return (
        select(models.Posts)
        .join(models.Users, models.Users.id == models.Posts.owner_id)
        .filter(models.Users.role == "anthony", models.Posts.published.is_(True))
        .order_by(models.Posts.id.desc())
    )


async def get_owned_post(post_id: int, owner_id: int, db: db_dependency):
    result = await db.execute(
        select(models.Posts).filter(
            models.Posts.id == post_id,
            models.Posts.owner_id == owner_id,
        )
    )
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.get("/")
async def root():
    return {
        "message": "AJK API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/healthy",
    }

@router.get("/posts")
async def read_public_posts(db: db_dependency):
    result = await db.execute(build_public_blog_statement())
    return result.scalars().all()

@router.get("/posts/blog")
async def read_public_blog_posts(db: db_dependency):
    result = await db.execute(build_public_blog_statement())
    return result.scalars().all()


@router.get("/posts/user/{user_id}")
async def read_posts_for_user(user_id: int, db: db_dependency):
    result = await db.execute(
        select(models.Posts)
        .filter(
            models.Posts.owner_id == user_id,
            models.Posts.published.is_(True),
        )
        .order_by(models.Posts.id.desc())
    )
    return result.scalars().all()


@router.get("/posts/me")
async def read_my_posts(user: user_dependency, db: db_dependency):
    result = await db.execute(
        select(models.Posts)
        .filter(models.Posts.owner_id == user["id"])
        .order_by(models.Posts.id.desc())
    )
    return result.scalars().all()

@router.post("/posts")
async def create_post(post: PostsRequest, user: user_dependency, db: db_dependency):
    new_post = models.Posts(
        title=post.title.strip(),
        content=(post.content or "").strip() or None,
        published=post.published if post.published is not None else True,
        owner_id=user["id"],
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


@router.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    post: PostsRequest,
    user: user_dependency,
    db: db_dependency,
):
    current_post = await get_owned_post(post_id, user["id"], db)
    current_post.title = post.title.strip()
    current_post.content = (post.content or "").strip() or None
    current_post.published = post.published if post.published is not None else True
    await db.commit()
    await db.refresh(current_post)
    return current_post


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, user: user_dependency, db: db_dependency):
    current_post = await get_owned_post(post_id, user["id"], db)
    await db.delete(current_post)
    await db.commit()
    return {"message": "Post deleted successfully", "id": post_id}
