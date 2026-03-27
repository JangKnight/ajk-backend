import models
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from database import db_dependency
from routers.auth import user_dependency


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)


class UpdateProfileRequest(BaseModel):
    about: str = Field(default="", max_length=4000)


def serialize_profile(user: models.Users) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "about": user.about or "",
    }


def serialize_public_profile(user: models.Users) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "about": user.about or "",
    }


@router.get("/me")
async def read_profile(user: user_dependency, db: db_dependency):
    current_user = await db.get(models.Users, user["id"])

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return serialize_profile(current_user)


@router.get("/{user_id}")
async def read_public_profile(user_id: int, db: db_dependency):
    current_user = await db.get(models.Users, user_id)

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return serialize_public_profile(current_user)


@router.put("/me")
async def update_profile(
    profile: UpdateProfileRequest,
    user: user_dependency,
    db: db_dependency,
):
    current_user = await db.get(models.Users, user["id"])

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    current_user.about = profile.about.strip()
    await db.commit()
    await db.refresh(current_user)

    return serialize_profile(current_user)
