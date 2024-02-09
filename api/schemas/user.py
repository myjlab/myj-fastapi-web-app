from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str = Field(..., example="a8199001@aoyama.jp")
    nickname: str | None = Field(None, example="tarou")


class UserCreate(UserBase):
    password: str = Field(..., example="1234")


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True
