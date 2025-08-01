from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship


class ActividadesGrupales(Base):
    __tablename__ = "ActividadesGrupales"

    id = Column(
        Integer,
        primary_key=True,
    )
    id_profesional = Column(
        Integer, ForeignKey("Profesionales.id_profesional"), nullable=True
    )
    id_tipo_actividad = Column(Integer, ForeignKey("TipoActividad.id"), nullable=True)
    comentarios = Column(String(255))
    descripcion = Column(String(255))
    duracion = Column(Integer)
    fecha = Column(Date)
    nombre = Column(String(50))
    profesional = relationship(
        "Profesionales", foreign_keys=[id_profesional], lazy="joined"
    )
    tipo_actividad = relationship(
        "TipoActividad", foreign_keys=[id_tipo_actividad], lazy="joined"
    )
    
    # Relación con usuarios asignados
    usuarios_asignados = relationship(
        "ActividadesUsuarios", 
        back_populates="actividad",
        cascade="all, delete-orphan"
    )

    class Config:
        orm_mode = True


class TipoActividad(Base):
    __tablename__ = "TipoActividad"

    id = Column(
        Integer,
        primary_key=True,
    )
    tipo = Column(String(50))

    class Config:
        orm_mode = True
