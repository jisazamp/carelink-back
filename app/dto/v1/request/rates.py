from pydantic import BaseModel, validator
from decimal import Decimal
from typing import List


class TarifaServicioUpdateDTO(BaseModel):
    id: int
    id_servicio: int
    anio: int
    precio_por_dia: Decimal

    @validator('precio_por_dia')
    def validate_precio_por_dia(cls, v):
        if v <= 0:
            raise ValueError('El precio por día debe ser mayor a 0')
        return v

    @validator('anio')
    def validate_anio(cls, v):
        if v < 2020 or v > 2030:
            raise ValueError('El año debe estar entre 2020 y 2030')
        return v

    @validator('id_servicio')
    def validate_id_servicio(cls, v):
        if v <= 0:
            raise ValueError('El ID de servicio debe ser válido')
        return v


class TarifasServicioUpdateRequestDTO(BaseModel):
    TarifasServicioPorAnio: List[TarifaServicioUpdateDTO]

    @validator('TarifasServicioPorAnio')
    def validate_tarifas(cls, v):
        if not v:
            raise ValueError('Debe proporcionar al menos una tarifa')
        return v 