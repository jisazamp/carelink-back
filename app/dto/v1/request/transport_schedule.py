from datetime import time
from pydantic import BaseModel
from typing import Optional


class CronogramaTransporteCreateDTO(BaseModel):
    id_cronograma_paciente: int
    direccion_recogida: Optional[str] = None
    direccion_entrega: Optional[str] = None
    hora_recogida: Optional[time] = None
    hora_entrega: Optional[time] = None
    observaciones: Optional[str] = None


class CronogramaTransporteUpdateDTO(BaseModel):
    direccion_recogida: Optional[str] = None
    direccion_entrega: Optional[str] = None
    hora_recogida: Optional[time] = None
    hora_entrega: Optional[time] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None


class RutaTransporteCreateDTO(BaseModel):
    fecha: str
    id_profesional: int
    rutas: list[dict]  # Lista de rutas con pacientes y horarios 