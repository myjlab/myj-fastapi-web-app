from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(db: Session, user: dict) -> dict:
    sql = text(
        """
        INSERT INTO users (email, nickname, password)
        VALUES (:email, :nickname, :password)
        """
    )
    params = {
        "email": user.get("email"),
        "nickname": user.get("nickname"),
        "password": get_password_hash(user.get("password")),
    }

    print(f"SQL: {sql}")
    db.execute(sql, params)
    db.commit()
    new_user = get_user_by_email(db, user.get("email"))
    print(f"DB操作の結果: {new_user}")

    return new_user


def get_user_by_email(db: Session, email: str) -> dict | None:
    sql = text(
        """
        SELECT * FROM users
        WHERE email = :email
        """
    )
    params = {"email": email}

    print(f"SQL: {sql}\nParams: {params}")
    result = db.execute(sql, params).first()
    if result is not None:
        result = result._asdict()
    print(f"DB操作の結果: {result}")

    return result


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> dict | bool:
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.get("password")):
        return False
    return user
