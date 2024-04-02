from sqlalchemy import select
from sqlalchemy.engine import Result, Row
from sqlalchemy.orm import Session

import api.models.task as task_model
import api.schemas.task as task_schema


def create_task(
    db: Session,
    task_create: task_schema.TaskCreate,
    user_id: int,
) -> task_model.Task:
    task = task_model.Task(**task_create.dict(), user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(
    db: Session,
    task_id: int,
) -> task_model.Task | None:
    result: Result = db.execute(
        select(task_model.Task).filter(task_model.Task.id == task_id)
    )
    return result.scalars().first()


def get_task_with_done(
    db: Session,
    task_id: int,
) -> Row | None:
    result: Result = db.execute(
        select(
            task_model.Task.id,
            task_model.Task.title,
            task_model.Task.due_date,
            task_model.Task.user_id,
            task_model.Task.img_path,
            task_model.Done.id.isnot(None).label("done"),
        )
        .filter(task_model.Task.id == task_id)
        .outerjoin(task_model.Done)
    )
    return result.first()


def get_multiple_tasks_with_done(
    db: Session,
    user_id: int,
) -> list[Row]:
    result: Result = db.execute(
        select(
            task_model.Task.id,
            task_model.Task.title,
            task_model.Task.due_date,
            task_model.Task.user_id,
            task_model.Done.id.isnot(None).label("done"),
        )
        .filter(task_model.Task.user_id == user_id)
        .outerjoin(task_model.Done)
    )

    return result.all()


def update_task(
    db: Session,
    task_create: task_schema.TaskDBUpdate,
    original: task_model.Task,
) -> task_model.Task:

    if task_create.title is not None:
        original.title = task_create.title

    if task_create.due_date is not None:
        original.due_date = task_create.due_date

    if task_create.img_path is not None:
        original.img_path = task_create.img_path

    db.add(original)
    db.commit()
    db.refresh(original)
    return original


def delete_task(db: Session, original: task_model.Task):
    db.delete(original)
    db.commit()
