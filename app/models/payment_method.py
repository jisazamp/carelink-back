from .base import Base
from sqlalchemy import Column, Integer, String


class MetodoPago(Base):
    __tablename__ = "MetodoPago"

    id_metodo_pago = Column(
        Integer,
        primary_key=True,
    )
    nombre = Column(String)

    class Config:
        orm_mode = True
