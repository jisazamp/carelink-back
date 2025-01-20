from .base import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


class FamilyMember(Base):
    __tablename__ = "Familiares"

    id_acudiente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    acudiente = Column(Boolean)
    apellidos = Column(String)
    direccion = Column(String)
    email = Column(String)
    n_documento = Column(String)
    nombres = Column(String)
    telefono = Column(String)
    vive = Column(Boolean)
    is_deleted = Column(Boolean)

    class Config:
        orm_mode = True
