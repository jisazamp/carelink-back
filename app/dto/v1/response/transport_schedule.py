from datetime import time, datetime
from pydantic import BaseModel
from typing import Optional


class CronogramaTransporteResponseDTO(BaseModel):
    id_transporte: int
    id_cronograma_paciente: int
    direccion_recogida: Optional[str]
    direccion_entrega: Optional[str]
    hora_recogida: Optional[time]
    hora_entrega: Optional[time]
    estado: str
    observaciones: Optional[str]
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        orm_mode = True


class RutaTransporteResponseDTO(BaseModel):
    id_transporte: int
    id_cronograma_paciente: int
    id_usuario: int
    nombres: str
    apellidos: str
    n_documento: str
    direccion_recogida: Optional[str]
    direccion_entrega: Optional[str]
    hora_recogida: Optional[time]
    hora_entrega: Optional[time]
    estado: str
    observaciones: Optional[str]

    class Config:
        orm_mode = True


class RutaDiariaResponseDTO(BaseModel):
    fecha: str
    id_profesional: int
    rutas: list[RutaTransporteResponseDTO]
    total_pacientes: int
    total_pendientes: int
    total_realizados: int
    total_cancelados: int

    class Config:
        orm_mode = True 