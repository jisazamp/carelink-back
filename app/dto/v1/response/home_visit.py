from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional
from decimal import Decimal


class VisitaDomiciliariaResponseDTO(BaseModel):
    id_visitadomiciliaria: int
    id_contrato: Optional[int] = None
    id_usuario: Optional[int] = None
    fecha_visita: Optional[date] = None
    hora_visita: Optional[time] = None
    estado_visita: str
    direccion_visita: str
    telefono_visita: Optional[str] = None
    valor_dia: Decimal
    observaciones: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True


class VisitaDomiciliariaConProfesionalResponseDTO(BaseModel):
    id_visitadomiciliaria: int
    id_contrato: Optional[int] = None
    id_usuario: Optional[int] = None
    fecha_visita: Optional[date] = None
    hora_visita: Optional[time] = None
    estado_visita: str
    direccion_visita: str
    telefono_visita: Optional[str] = None
    valor_dia: Decimal
    observaciones: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    profesional_asignado: Optional[str] = None  # Nombre del profesional asignado

    class Config:
        orm_mode = True 