from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from api.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    nickname = Column(String(64))
    password = Column(String(64))

    tasks = relationship("Task", back_populates="user", cascade="delete")
