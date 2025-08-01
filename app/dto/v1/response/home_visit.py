from pydantic import BaseModel, validator
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

    @validator('fecha_visita', pre=True)
    def format_fecha_visita(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v.strftime('%Y-%m-%d')
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d')
        return str(v) if v else None

    @validator('hora_visita', pre=True)
    def format_hora_visita(cls, v):
        if v is None:
            return None
        if isinstance(v, time):
            return v.strftime('%H:%M:%S')
        if isinstance(v, datetime):
            return v.strftime('%H:%M:%S')
        return str(v) if v else None

    @validator('fecha_creacion', pre=True)
    def format_fecha_creacion(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return str(v) if v else None

    @validator('fecha_actualizacion', pre=True)
    def format_fecha_actualizacion(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return str(v) if v else None

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

    @validator('fecha_visita', pre=True)
    def format_fecha_visita(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v.strftime('%Y-%m-%d')
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d')
        return str(v) if v else None

    @validator('hora_visita', pre=True)
    def format_hora_visita(cls, v):
        if v is None:
            return None
        if isinstance(v, time):
            return v.strftime('%H:%M:%S')
        if isinstance(v, datetime):
            return v.strftime('%H:%M:%S')
        return str(v) if v else None

    @validator('fecha_creacion', pre=True)
    def format_fecha_creacion(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return str(v) if v else None

    @validator('fecha_actualizacion', pre=True)
    def format_fecha_actualizacion(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return str(v) if v else None

    @validator('fecha_asignacion', pre=True)
    def format_fecha_asignacion(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return str(v) if v else None

    class Config:
        orm_mode = True 
