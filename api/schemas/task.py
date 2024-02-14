import datetime

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    title: str | None = Field(..., example="クリーニングを取りに行く")
    due_date: datetime.date | None = Field(None, example="2024-12-01")


class TaskCreate(TaskBase):
    pass


class TaskCreateResponse(TaskCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class Task(TaskCreateResponse):
    done: bool = Field(False, description="完了フラグ")
