from pydantic import BaseModel
from decimal import Decimal
from typing import List


class TarifaServicioResponseDTO(BaseModel):
    id: int
    id_servicio: int
    anio: int
    precio_por_dia: Decimal
    nombre_servicio: str = None

    class Config:
        orm_mode = True


class TarifasServicioResponseDTO(BaseModel):
    TarifasServicioPorAnio: List[TarifaServicioResponseDTO]

    class Config:
        orm_mode = True
