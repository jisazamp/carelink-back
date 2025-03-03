from pydantic import BaseModel
from datetime import date


class ProfessionalResponse(BaseModel):
    id_profesional: int
    apellidos: str
    cargo: str
    direccion: str
    e_mail: str
    especialidad: str
    estado: str
    fecha_ingreso: date
    fecha_nacimiento: date
    n_documento: str
    nombres: str
    profesion: str
    t_profesional: str
    telefono: int

    class Config:
        orm_mode = True
