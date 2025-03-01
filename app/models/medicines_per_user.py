from .base import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey


class MedicamentosPorUsuario(Base):
    __tablename__ = "MedicamentosPorUsuario"

    id = Column(
        Integer,
        primary_key=True,
    )
    id_historiaClinica = Column(
        Integer, ForeignKey("HistoriaClinica.id_historiaclinica"), primary_key=True
    )
    medicamento = Column(String)
    periodicidad = Column(String)
    Fecha_inicio = Column(Date)
    fecha_fin = Column(Date)

    class Config:
        orm_mode = True
