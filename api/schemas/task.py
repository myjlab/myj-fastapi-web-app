import datetime

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    title: str = Field(..., example="クリーニングを取りに行く")
    due_date: datetime.date | None = Field(None, example="2024-12-01")


class TaskCreate(TaskBase):
    pass


class TaskCreateResponse(TaskCreate):
    id: int
    user_id: int
    img_path: str | None = Field(
        None,
        example="/static/images/2024-02-19T13:26:57.766065_643fbb.png",
    )

    class Config:
        orm_mode = True


class TaskApiUpdate(BaseModel):
    title: str | None
    due_date: datetime.date | None


class TaskDBUpdate(TaskApiUpdate):
    img_path: str | None


class Task(TaskCreateResponse):
    done: bool = Field(False, description="完了フラグ")
