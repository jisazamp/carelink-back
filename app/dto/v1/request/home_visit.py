from pydantic import BaseModel, validator
from datetime import date, time
from typing import Optional
from decimal import Decimal


class VisitaDomiciliariaCreateDTO(BaseModel):
    id_usuario: int
    fecha_visita: date
    hora_visita: time
    direccion_visita: str
    telefono_visita: Optional[str] = None
    valor_dia: Decimal
    observaciones: Optional[str] = None
    id_profesional_asignado: Optional[int] = None

    @validator('valor_dia')
    def validate_valor_dia(cls, v):
        if v <= 0:
            raise ValueError('El valor del día debe ser mayor a 0')
        return v

    @validator('fecha_visita')
    def validate_fecha_visita(cls, v):
        if v < date.today():
            raise ValueError('La fecha de visita no puede ser anterior a hoy')
        return v


class VisitaDomiciliariaUpdateDTO(BaseModel):
    fecha_visita: Optional[date] = None
    hora_visita: Optional[time] = None
    estado_visita: Optional[str] = None
    direccion_visita: Optional[str] = None
    telefono_visita: Optional[str] = None
    valor_dia: Optional[Decimal] = None
    observaciones: Optional[str] = None

    @validator('valor_dia')
    def validate_valor_dia(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El valor del día debe ser mayor a 0')
        return v

    @validator('fecha_visita')
    def validate_fecha_visita(cls, v):
        if v is not None and v < date.today():
            raise ValueError('La fecha de visita no puede ser anterior a hoy')
        return v

    @validator('estado_visita')
    def validate_estado_visita(cls, v):
        if v is not None and v not in ['PENDIENTE', 'REALIZADA', 'CANCELADA', 'REPROGRAMADA']:
            raise ValueError('Estado de visita inválido')
        return v 