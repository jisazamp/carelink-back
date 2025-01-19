from .base import Base
from sqlalchemy import Column, Integer, String


class AuthorizedUsers(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)

    class Config:
        orm_mode = True
