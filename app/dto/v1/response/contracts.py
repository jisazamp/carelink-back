from datetime import date
from pydantic import BaseModel
from typing import List


class FechaServicioDTO(BaseModel):
    fecha: date

    class Config:
        orm_mode = True


class ServicioContratoDTO(BaseModel):
    id_servicio_contratado: int
    id_servicio: int
    fecha: date
    descripcion: str
    precio_por_dia: float
    fechas_servicio: List[FechaServicioDTO]

    class Config:
        orm_mode = True


class ContratoResponseDTO(BaseModel):
    id_contrato: int
    tipo_contrato: str
    fecha_inicio: date
    fecha_fin: date
    facturar_contrato: bool
    servicios: List[ServicioContratoDTO]

    class Config:
        orm_mode = True
