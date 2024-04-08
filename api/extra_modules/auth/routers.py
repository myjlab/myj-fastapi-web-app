from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import api.cruds.user as user_crud
import api.extra_modules.auth.schema as auth_schemas
from api.db import get_db
from api.extra_modules.auth.core import create_access_token

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
router = APIRouter()


@router.post("/token")
def login_for_access_token(
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> auth_schemas.Token:
    """
    OAuth2互換のtokenログイン、access tokenを返す。

    同時にtokenをクッキー"Authorization"に設定します。
    """
    user = user_crud.authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )

    response.set_cookie(
        key="Authorization",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return auth_schemas.Token(access_token=access_token, token_type="bearer")
