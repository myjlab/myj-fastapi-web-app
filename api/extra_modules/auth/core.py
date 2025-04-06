import typing as T
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import api.cruds.user as user_crud
import api.extra_modules.auth.schema as auth_schemas
from api.db import get_db

# ! 本当は環境変数などから取得するべき
SECRET_KEY = "6ae97a28c3884986c02e1160313d30c2a065bbc4b14e4f6400085dd3e8afa6ea"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def create_access_token(
    data: dict,
    expires_delta: T.Union[timedelta, None] = None,
) -> str:

    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=15)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
):
    """
    tokenを検証し、userを返します。

    tokenはheaderのAuthorizationから取得します。
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    email = payload.get("sub")
    if email is None:
        raise credentials_exception

    token_data = auth_schemas.TokenData(email=email)

    user = user_crud.get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception

    return user
