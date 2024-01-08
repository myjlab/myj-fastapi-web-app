from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import api.cruds.done as done_crud
import api.schemas.done as done_schema
from api.db import get_db

router = APIRouter()


@router.put("/tasks/{task_id}/done", response_model=done_schema.DoneResponse)
def mark_task_as_done(
    task_id: int,
    db: Session = Depends(get_db),
):
    done = done_crud.get_done(db, task_id=task_id)
    if done is not None:
        raise HTTPException(status_code=400, detail="Done already exists")

    return done_crud.create_done(db, task_id)


@router.delete("/tasks/{task_id}/done", response_model=None)
def unmark_task_as_done(
    task_id: int,
    db: Session = Depends(get_db),
):
    done = done_crud.get_done(db, task_id=task_id)
    if done is None:
        raise HTTPException(status_code=404, detail="Done not found")

    return done_crud.delete_done(db, original=done)
