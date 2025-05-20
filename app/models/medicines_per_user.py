from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey


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
    observaciones = Column(String)

    class Config:
        orm_mode = True
