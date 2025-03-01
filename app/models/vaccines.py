from .base import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text


class VacunasPorUsuario(Base):
    __tablename__ = "VacunasPorUsuario"

    id = Column(
        Integer,
        primary_key=True,
    )
    id_historiaClinica = Column(
        Integer, ForeignKey("HistoriaClinica.id_historiaclinica"), primary_key=True
    )
    efectos_secundarios = Column(Text)
    fecha_administracion = Column(Date, nullable=True)
    fecha_proxima = Column(Date, nullable=True)
    vacuna = Column(String)

    class Config:
        orm_mode = True
