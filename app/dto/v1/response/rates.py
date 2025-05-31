from pydantic import BaseModel
from datetime import date


class ServiceRatesResponseDTO(BaseModel):
    id: int
    id_servicio: int
    anio: date
    precio_por_dia: float

    class Config:
        orm_mode = True
