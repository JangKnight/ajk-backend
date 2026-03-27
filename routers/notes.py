import models
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from typing import Optional

from database import db_dependency
from routers.auth import user_dependency


router = APIRouter(
    prefix="/notes",
    tags=["notes"],
)


class NoteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    content: Optional[str] = Field(default="", max_length=4000)


async def get_owned_note(note_id: int, owner_id: int, db: db_dependency):
    statement = select(models.Notes).filter(
        models.Notes.id == note_id,
        models.Notes.owner_id == owner_id,
    )
    result = await db.execute(statement)
    note = result.scalars().first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    return note


@router.get("")
async def read_notes(user: user_dependency, db: db_dependency):
    statement = (
        select(models.Notes)
        .filter(models.Notes.owner_id == user["id"])
        .order_by(models.Notes.id.desc())
    )
    result = await db.execute(statement)
    return result.scalars().all()


@router.post("")
async def create_note(note: NoteRequest, user: user_dependency, db: db_dependency):
    new_note = models.Notes(
        title=note.title.strip(),
        content=(note.content or "").strip(),
        owner_id=user["id"],
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note


@router.put("/{note_id}")
async def update_note(
    note_id: int,
    note: NoteRequest,
    user: user_dependency,
    db: db_dependency,
):
    current_note = await get_owned_note(note_id, user["id"], db)
    current_note.title = note.title.strip()
    current_note.content = (note.content or "").strip()
    await db.commit()
    await db.refresh(current_note)
    return current_note


@router.delete("/{note_id}")
async def delete_note(note_id: int, user: user_dependency, db: db_dependency):
    current_note = await get_owned_note(note_id, user["id"], db)
    await db.delete(current_note)
    await db.commit()
    return {"message": "Note deleted successfully", "id": note_id}
