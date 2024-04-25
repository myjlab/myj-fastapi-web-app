from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

import api.cruds.task as task_crud
import api.schemas.task as task_schema
from api.db import get_db
from api.extra_modules.auth.core import get_current_user
from api.extra_modules.image.core import save_image
from api.models.user import User as UserModel

router = APIRouter()


@router.post("/task", response_model=task_schema.TaskCreateResponse)
def create_task(
    task_body: task_schema.TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return task_crud.create_task(db, task_body, current_user.id)


@router.get("/tasks", response_model=list[task_schema.Task])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return task_crud.get_multiple_tasks_with_done(db, current_user.id)


@router.get("/task/{task_id}", response_model=task_schema.Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = task_crud.get_task_with_done(db, task_id=task_id)

    # タスクが存在しない場合
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_schema.Task.from_orm(task)
    # 他のユーザーのタスクを取得しようとした場合
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return task


@router.put("/task/{task_id}", response_model=task_schema.TaskCreateResponse)
def update_task(
    task_id: int,
    task_body: task_schema.TaskApiUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = task_crud.get_task(db, task_id=task_id)

    # タスクが存在しない場合
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # 他のユーザーのタスクを変更しようとした場合
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return task_crud.update_task(
        db,
        task_schema.TaskDBUpdate(**task_body.dict()),
        original=task,
    )


@router.put(
    "/task/{task_id}/image",
    response_model=task_schema.TaskCreateResponse,
)
def add_image_to_task(
    task_id: int,
    image: UploadFile,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = task_crud.get_task(db, task_id=task_id)

    # タスクが存在しない場合
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    #  他のユーザーのタスクを変更しようとした場合
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    img_path = save_image(image)

    return task_crud.update_task(
        db,
        task_schema.TaskDBUpdate(img_path=img_path),
        original=task,
    )


@router.delete("/task/{task_id}", response_model=None)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = task_crud.get_task(db, task_id=task_id)

    # タスクが存在しない場合
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # 他のユーザーのタスクを削除しようとした場合
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return task_crud.delete_task(db, original=task)
