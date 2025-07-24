from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional


class HomeVisitResponseDTO(BaseModel):
    id_visitadomiciliaria: int
    id_contrato: Optional[int] = None
    id_usuario: int
    fecha_visita: date
    hora_visita: time
    estado_visita: str
    direccion_visita: str
    telefono_visita: Optional[str] = None
    valor_dia: float
    observaciones: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True 