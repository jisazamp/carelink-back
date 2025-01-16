from app.database.connection import carelink_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    bind = carelink_engine
