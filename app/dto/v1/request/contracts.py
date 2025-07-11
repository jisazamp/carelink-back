from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import List, Optional

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
    impuestos: Optional[float] = 0.0
    descuentos: Optional[float] = 0.0


class ContratoUpdateDTO(BaseModel):
    tipo_contrato: Optional[str]
    fecha_inicio: Optional[date]
    fecha_fin: Optional[date]
    facturar_contrato: Optional[bool]
    servicios: List[ServicioContratadoCreateDTO]


class PagoCreateDTO(BaseModel):
    id_factura: int
    id_metodo_pago: int
    id_tipo_pago: int
    fecha_pago: date
    valor: Decimal = Field(..., gt=0, decimal_places=2)


class PagoResponseDTO(BaseModel):
    id_pago: int
    id_factura: int
    id_metodo_pago: int
    id_tipo_pago: int
    fecha_pago: date
    valor: float

    class Config:
        orm_mode = True


class PagoCreate(BaseModel):
    id_metodo_pago: int
    id_tipo_pago: int
    fecha_pago: date
    valor: Decimal


class FacturaCreate(BaseModel):
    id_contrato: int
    fecha_emision: date
    fecha_vencimiento: date
    total: Decimal
    pagos: Optional[List[PagoCreate]] = []


class FacturaCreateWithDetails(BaseModel):
    """
    DTO para crear facturas con datos completos incluyendo impuestos y descuentos
    """
    impuestos: float = 0.0
    descuentos: float = 0.0
    observaciones: Optional[str] = ""
    
    class Config:
        schema_extra = {
            "example": {
                "impuestos": 5000.0,
                "descuentos": 2000.0,
                "observaciones": "Factura generada automáticamente desde el contrato"
            }
        }
