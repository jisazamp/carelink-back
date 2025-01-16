from sqlalchemy import Column, Integer, String

from .base import Base


class User(Base):
    __tablename__ = "Usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    apellidos = Column(String(50))
    n_documento = Column(String(255))
    nombres = Column(String(50))

    class Config:
        orm_mode = True
