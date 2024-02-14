from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import api.cruds.done as done_crud
import api.cruds.task as task_crud
import api.schemas.done as done_schema
from api.auth.core import get_current_user
from api.db import get_db
from api.models.user import User as UserModel

router = APIRouter()


@router.put("/tasks/{task_id}/done", response_model=done_schema.DoneResponse)
def mark_task_as_done(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = task_crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    done = done_crud.get_done(db, task_id=task_id)
    if done is not None:
        raise HTTPException(status_code=400, detail="Done already exists")

    return done_crud.create_done(db, task_id)


@router.delete("/tasks/{task_id}/done", response_model=None)
def unmark_task_as_done(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):

    done = done_crud.get_done(db, task_id=task_id)
    if done is None:
        raise HTTPException(status_code=404, detail="Not found")

    task = task_crud.get_task(db, task_id=task_id)
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return done_crud.delete_done(db, original=done)
