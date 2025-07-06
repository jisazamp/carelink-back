from sqlalchemy import Column, Integer, String, Text, Time, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class EstadoTransporte(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    REALIZADO = "REALIZADO"
    CANCELADO = "CANCELADO"

class CronogramaTransporte(Base):
    __tablename__ = "cronograma_transporte"

    id_transporte = Column(Integer, primary_key=True, index=True)
    id_cronograma_paciente = Column(Integer, ForeignKey("cronograma_asistencia_pacientes.id_cronograma_paciente"), nullable=False)
    direccion_recogida = Column(Text)
    direccion_entrega = Column(Text)
    hora_recogida = Column(Time)
    hora_entrega = Column(Time)
    estado = Column(Enum(EstadoTransporte), default=EstadoTransporte.PENDIENTE)
    observaciones = Column(Text)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con el cronograma de asistencia
    cronograma_paciente = relationship("CronogramaAsistenciaPacientes", back_populates="transporte") 