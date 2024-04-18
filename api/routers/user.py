from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import api.cruds.user as user_crud
import api.schemas.user as user_schema
from api.db import get_db
from api.extra_modules.auth.core import get_current_user

router = APIRouter()


@router.post("/user", response_model=user_schema.UserResponse)
def create_user(
    user: user_schema.UserCreate,
    db: Session = Depends(get_db),
):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    # すでに登録されているメールアドレスの場合
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create_user(db, user)


@router.get("/me", response_model=user_schema.UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user
