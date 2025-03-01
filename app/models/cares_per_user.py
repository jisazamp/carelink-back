from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey


class CuidadosEnfermeriaPorUsuario(Base):
    __tablename__ = "CuidadosEnfermeriaPorUsuario"

    id = Column(
        Integer,
        primary_key=True,
    )
    id_historiaClinica = Column(
        Integer, ForeignKey("HistoriaClinica.id_historiaclinica"), primary_key=True
    )
    diagnostico = Column(String)
    frecuencia = Column(String)
    intervencion = Column(String)

    class Config:
        orm_mode = True
