from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Body
from sqlalchemy.orm import Session

import api.cruds.task as task_crud
from api.db import get_db
from api.extra_modules.auth.core import get_current_user
from api.extra_modules.image.core import save_image

router = APIRouter()


@router.post("/task")
def create_task(
    task_body=Body(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    print("受けたデータ\n", task_body)

    try:
        due_date = task_body.get("due_date")
        if due_date is not None:
            datetime.strptime(task_body.get("due_date"), "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid due_date format")
    res = task_crud.create_task(db, task_body, user_id=current_user.get("id"))

    print("返すデータ\n", res)
    return res


@router.get("/tasks")
def list_tasks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return task_crud.get_multiple_tasks_with_done(db, current_user.get("id"))


@router.get("/task/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = task_crud.get_task_with_done(db, task_id=task_id)

    # タスクが存在しない場合
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # 他のユーザーのタスクを取得しようとした場合
    if task.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    return task


@router.put("/task/{task_id}")
def update_task(
    task_id: int,
    task_body: dict = Body(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    print("受けたデータ\n", task_body)

    task = task_crud.get_task(db, task_id=task_id)

    # タスクが存在しない場合
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # 他のユーザーのタスクを変更しようとした場合
    if task.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    if "img_path" in task_body:
        del task_body["img_path"]

    new_task = task_crud.update_task(
        db,
        task_body,
        original=task,
    )

    print("返すデータ\n", new_task)
    return new_task


@router.put("/task/{task_id}/image")
def add_image_to_task(
    task_id: int,
    image: UploadFile,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = task_crud.get_task(db, task_id=task_id)

    # タスクが存在しない場合
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    #  他のユーザーのタスクを変更しようとした場合
    if task.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    img_path = save_image(image)

    return task_crud.update_task(
        db,
        {"img_path": img_path},
        original=task,
    )


@router.delete("/task/{task_id}", response_model=None)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = task_crud.get_task(db, task_id=task_id)

    # タスクが存在しない場合
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # 他のユーザーのタスクを削除しようとした場合
    if task.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    return task_crud.delete_task(db, original=task)
