from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional
from decimal import Decimal


class VisitaDomiciliariaResponseDTO(BaseModel):
    id_visitadomiciliaria: int
    id_contrato: Optional[int] = None
    id_usuario: Optional[int] = None
    fecha_visita: Optional[str] = None
    hora_visita: Optional[str] = None
    estado_visita: str
    direccion_visita: str
    telefono_visita: Optional[str] = None
    valor_dia: Decimal
    observaciones: Optional[str] = None
    fecha_creacion: str
    fecha_actualizacion: str

    class Config:
        orm_mode = True


class VisitaDomiciliariaConProfesionalResponseDTO(BaseModel):
    id_visitadomiciliaria: int
    id_contrato: Optional[int] = None
    id_usuario: Optional[int] = None
    fecha_visita: Optional[str] = None
    hora_visita: Optional[str] = None
    estado_visita: str
    direccion_visita: str
    telefono_visita: Optional[str] = None
    valor_dia: Decimal
    observaciones: Optional[str] = None
    fecha_creacion: str
    fecha_actualizacion: str
    # Campos del usuario
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    n_documento: Optional[str] = None
    telefono: Optional[str] = None
    # Campos del profesional
    profesional_nombres: Optional[str] = None
    profesional_especialidad: Optional[str] = None
    estado_asignacion: Optional[str] = None
    fecha_asignacion: Optional[str] = None
    # Campos calculados
    profesional_asignado: Optional[str] = None  # Nombre del profesional asignado
    paciente_nombre: Optional[str] = None  # Nombre completo del paciente

    class Config:
        orm_mode = True 