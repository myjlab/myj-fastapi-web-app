from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import api.cruds.task as task_crud
import api.schemas.task as task_schema
from api.db import get_db

router = APIRouter()


@router.get("/tasks", response_model=list[task_schema.Task])
def list_tasks(db: Session = Depends(get_db)):
    return task_crud.get_tasks_with_done(db)


@router.post("/tasks", response_model=task_schema.TaskCreateResponse)
def create_task(
    task_body: task_schema.TaskCreate,
    db: Session = Depends(get_db),
):
    return task_crud.create_task(db, task_body)


@router.put("/tasks/{task_id}", response_model=task_schema.TaskCreateResponse)
def update_task(
    task_id: int,
    task_body: task_schema.TaskCreate,
    db: Session = Depends(get_db),
):
    task = task_crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_crud.update_task(db, task_body, original=task)


@router.delete("/tasks/{task_id}", response_model=None)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = task_crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_crud.delete_task(db, original=task)
