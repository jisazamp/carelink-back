from .base import Base
from sqlalchemy import Column, Integer, Date, Text, ForeignKey, Enum, String, Boolean
from sqlalchemy.orm import relationship

class CronogramaAsistencia(Base):
    __tablename__ = "cronograma_asistencia"
    id_cronograma = Column(Integer, primary_key=True)
    id_profesional = Column(Integer, ForeignKey("users.id"))
    fecha = Column(Date, nullable=False)
    comentario = Column(Text)

    pacientes = relationship("CronogramaAsistenciaPacientes", back_populates="cronograma")

class CronogramaAsistenciaPacientes(Base):
    __tablename__ = "cronograma_asistencia_pacientes"
    id_cronograma_paciente = Column(Integer, primary_key=True)
    id_cronograma = Column(Integer, ForeignKey("cronograma_asistencia.id_cronograma"))
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"))
    id_contrato = Column(Integer, ForeignKey("Contratos.id_contrato"))
    estado_asistencia = Column(String(20), default="PENDIENTE")
    requiere_transporte = Column(Boolean, default=False)
    observaciones = Column(Text, nullable=True)

    cronograma = relationship("CronogramaAsistencia", back_populates="pacientes")
    transporte = relationship("CronogramaTransporte", back_populates="cronograma_paciente", uselist=False)
