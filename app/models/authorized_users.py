from .base import Base
from sqlalchemy import Boolean, Column, Integer, String


class AuthorizedUsers(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String)
    first_name = Column(String)
    is_deleted = Column(Boolean)
    last_name = Column(String)
    password = Column(String)
    role = Column(String)

    class Config:
        orm_mode = True
