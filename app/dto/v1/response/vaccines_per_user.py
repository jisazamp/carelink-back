from datetime import date
from pydantic import BaseModel


class VaccinesPerUserResponseDTO(BaseModel):
    id: int
    efectos_secundarios: str | None
    fecha_administracion: date | None
    fecha_proxima: date | None
    vacuna: str


class VaccinesPerUserUpdateDTO(BaseModel):
    efectos_secundarios: str | None
    fecha_administracion: date | None
    fecha_proxima: date | None
    vacuna: str | None
