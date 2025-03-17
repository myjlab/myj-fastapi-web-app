from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

import api.cruds.user as user_crud
from api.db import get_db
from api.extra_modules.auth.core import get_current_user

router = APIRouter()


@router.post("/user")
def create_user(
    user: dict = Body(),
    db: Session = Depends(get_db),
):
    print(f"受けたデータ:\n{user}")

    db_user = user_crud.get_user_by_email(db, email=user.get("email"))
    # すでに登録されているメールアドレスの場合
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_db_user = user_crud.create_user(db, user)
    return_user = {
        "id": new_db_user.get("id"),
        "email": new_db_user.get("email"),
        "nickname": new_db_user.get("nickname"),
    }

    print(f"返すデータ:\n{return_user}")
    return return_user


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/user/test")
def test(db: Session = Depends(get_db)):
    return user_crud.get_user_by_email(db, email="u1@aoyama.jp")
