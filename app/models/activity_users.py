from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from .base import Base


class ActividadesUsuarios(Base):
    __tablename__ = "ActividadesUsuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_actividad = Column(Integer, ForeignKey("ActividadesGrupales.id"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)
    estado_participacion = Column(
        Enum('CONFIRMADO', 'PENDIENTE', 'CANCELADO', name='estado_participacion_enum'),
        default='PENDIENTE'
    )
    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    actividad = relationship("ActividadesGrupales", back_populates="usuarios_asignados")
    usuario = relationship("User", back_populates="actividades_asignadas")

    class Config:
        orm_mode = True 