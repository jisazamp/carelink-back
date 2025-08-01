from sqlalchemy import Column, Integer, Date, Time, String, Text, DECIMAL, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .base import Base


class VisitasDomiciliarias(Base):
    __tablename__ = "VisitasDomiciliarias"

    id_visitadomiciliaria = Column(Integer, primary_key=True, autoincrement=True)
    id_contrato = Column(Integer, ForeignKey("Contratos.id_contrato"), nullable=True)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=True)
    fecha_visita = Column(Date, nullable=True)
    hora_visita = Column(Time, nullable=True)
    estado_visita = Column(
        Enum("PENDIENTE", "REALIZADA", "CANCELADA", "REPROGRAMADA", name="estado_visita_enum"),
        nullable=False,
        default="PENDIENTE"
    )
    direccion_visita = Column(String(255), nullable=False)
    telefono_visita = Column(String(20), nullable=True)
    valor_dia = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    contrato = relationship("Contratos")
    usuario = relationship("User", back_populates="visitas_domiciliarias_list")


class VisitasDomiciliariasPorProfesional(Base):
    __tablename__ = "VisitasDomiciliariasPorProfesional"

    id_visitadomiciliaria = Column(Integer, ForeignKey("VisitasDomiciliarias.id_visitadomiciliaria"), primary_key=True)
    id_profesional = Column(Integer, ForeignKey("Profesionales.id_profesional"), primary_key=True)
    fecha_asignacion = Column(DateTime(timezone=True), server_default=func.now())
    estado_asignacion = Column(String(50))
    observaciones_asignacion = Column(Text)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    visita_domiciliaria = relationship("VisitasDomiciliarias")
    profesional = relationship("Profesionales") 
