from datetime import date
from pydantic import BaseModel
from typing import List, Optional


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
    id_usuario: int
    tipo_contrato: str
    fecha_inicio: date
    fecha_fin: date
    facturar_contrato: bool
    servicios: Optional[List[ServicioContratoDTO]]

    class Config:
        orm_mode = True


class FacturaOut(BaseModel):
    id_factura: int
    id_contrato: int | None
    fecha_emision: date
    total_factura: float

    class Config:
        orm_mode = True
