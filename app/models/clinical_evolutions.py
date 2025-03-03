from .base import Base
from sqlalchemy import Column, Integer, Date, ForeignKey, Text
from sqlalchemy.orm import relationship


class EvolucionesClinicas(Base):
    __tablename__ = "EvolucionesClinicas"

    id_TipoReporte = Column(Integer, primary_key=True, autoincrement=True)
    id_reporteclinico = Column(
        Integer, ForeignKey("ReportesClinicos.id_reporteclinico")
    )
    id_profesional = Column(Integer, ForeignKey("Profesionales.id_profesional"))
    fecha_evolucion = Column(Date)
    observacion_evolucion = Column(Text)
    tipo_report = Column(Text)
    profesional = relationship("Profesionales", foreign_keys=[id_profesional])

    class Config:
        orm_mode = True
