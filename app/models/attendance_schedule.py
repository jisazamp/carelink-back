from .base import Base
from sqlalchemy import Column, Integer, Date, Text, ForeignKey, Enum, String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

class EstadoAsistencia(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    ASISTIO = "ASISTIO"
    NO_ASISTIO = "NO_ASISTIO"
    CANCELADO = "CANCELADO"
    REAGENDADO = "REAGENDADO"

class CronogramaAsistencia(Base):
    __tablename__ = "cronograma_asistencia"
    
    id_cronograma = Column(Integer, primary_key=True, index=True)
    id_profesional = Column(Integer, ForeignKey("Profesionales.id_profesional"), nullable=False)
    fecha = Column(Date, nullable=False)
    comentario = Column(Text, nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relaciones
    pacientes = relationship("CronogramaAsistenciaPacientes", back_populates="cronograma", cascade="all, delete-orphan")
    profesional = relationship("Profesionales", foreign_keys=[id_profesional])

    class Config:
        orm_mode = True

class CronogramaAsistenciaPacientes(Base):
    __tablename__ = "cronograma_asistencia_pacientes"
    
    id_cronograma_paciente = Column(Integer, primary_key=True, index=True)
    id_cronograma = Column(Integer, ForeignKey("cronograma_asistencia.id_cronograma"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    id_contrato = Column(Integer, ForeignKey("Contratos.id_contrato"), nullable=False)
    estado_asistencia = Column(Enum(EstadoAsistencia), default=EstadoAsistencia.PENDIENTE)
    requiere_transporte = Column(Boolean, default=False)
    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relaciones
    cronograma = relationship("CronogramaAsistencia", back_populates="pacientes")
    usuario = relationship("User", foreign_keys=[id_usuario])
    contrato = relationship("Contratos", foreign_keys=[id_contrato])
    transporte = relationship("CronogramaTransporte", back_populates="cronograma_paciente", uselist=False, cascade="all, delete-orphan")

    class Config:
        orm_mode = True
