from datetime import date
from pydantic import BaseModel
from typing import List


class FechaServicioCreateDTO(BaseModel):
    fecha: date


class ServicioContratadoCreateDTO(BaseModel):
    id_servicio: int
    fecha: date
    descripcion: str
    precio_por_dia: float
    fechas_servicio: List[FechaServicioCreateDTO]


class ContratoCreateDTO(BaseModel):
    id_usuario: int
    tipo_contrato: str
    fecha_inicio: date
    fecha_fin: date
    facturar_contrato: bool
    servicios: List[ServicioContratadoCreateDTO]
