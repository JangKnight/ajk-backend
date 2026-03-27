import models
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from database import db_dependency
from routers.auth import user_dependency


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def ensure_anthony(user: dict) -> None:
    if user.get("role") != "anthony":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


def serialize_user(user: models.Users) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "about": user.about or "",
    }


def serialize_post(post: models.Posts, owner_username: str | None) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "published": post.published,
        "owner_id": post.owner_id,
        "owner_username": owner_username,
    }


@router.get("/users")
async def read_all_users(user: user_dependency, db: db_dependency):
    ensure_anthony(user)
    result = await db.execute(select(models.Users).order_by(models.Users.id.asc()))
    return [serialize_user(row) for row in result.scalars().all()]


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, user: user_dependency, db: db_dependency):
    ensure_anthony(user)

    if user_id == user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    existing_user = await db.get(models.Users, user_id)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(existing_user)
    await db.commit()
    return {"message": "User deleted successfully", "id": user_id}


@router.get("/posts")
async def read_all_posts(user: user_dependency, db: db_dependency):
    ensure_anthony(user)
    result = await db.execute(
        select(models.Posts, models.Users.username)
        .outerjoin(models.Users, models.Users.id == models.Posts.owner_id)
        .order_by(models.Posts.id.desc())
    )
    return [serialize_post(post, owner_username) for post, owner_username in result.all()]


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, user: user_dependency, db: db_dependency):
    ensure_anthony(user)
    existing_post = await db.get(models.Posts, post_id)

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    await db.delete(existing_post)
    await db.commit()
    return {"message": "Post deleted successfully", "id": post_id}
