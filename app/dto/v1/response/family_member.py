from pydantic import BaseModel
from typing import Optional


class FamilyMemberResponseDTO(BaseModel):
    id_acudiente: int
    acudiente: bool
    apellidos: str
    direccion: str
    email: str
    n_documento: str
    nombres: str
    telefono: str
    vive: bool
    parentesco: Optional[str]

    class Config:
        orm_mode = True
