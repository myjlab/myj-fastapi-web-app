from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session

import api.models.user as user_model
import api.schemas.user as user_schema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(db: Session, user: user_schema.UserCreate) -> user_model.User:
    user.password = get_password_hash(user.password)
    db_user = user_model.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> user_model.User | None:
    result: Result = db.execute(
        select(user_model.User).filter(user_model.User.email == email)
    )
    return result.scalars().first()


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> user_model.User | bool:
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
