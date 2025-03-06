from app.dto.v1.response.professional import ProfessionalResponse
from datetime import date
from pydantic import BaseModel


class TypeOfActivityResponse(BaseModel):
    id: int
    tipo: str | None

    class Config:
        orm_mode = True


class ActivitiesResponse(BaseModel):
    id: int
    id_profesional: int | None
    id_tipo_actividad: int | None
    comentarios: str | None
    descripcion: str | None
    duracion: int | None
    fecha: date | None
    nombre: str | None
    profesional: ProfessionalResponse | None
    tipo_actividad: TypeOfActivityResponse | None

    class Config:
        orm_mode = True
