from .base import Base
from sqlalchemy import Column, Integer, Float, ForeignKey, Date


class TarifasServicioPorAnio(Base):
    __tablename__ = "TarifasServicioPorAnio"

    id = Column(
        Integer,
        primary_key=True,
    )
    id_servicio = Column(Integer, ForeignKey("Servicios.id_servicio"), nullable=True)
    anio = Column(Date)
    precio_por_dia = Column(Float)

    class Config:
        orm_mode = True
