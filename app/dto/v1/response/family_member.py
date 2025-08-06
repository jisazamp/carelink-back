from pydantic import BaseModel
from typing import Optional


class FamilyMemberResponseDTO(BaseModel):
    id_acudiente: int
    acudiente: bool
    apellidos: Optional[str] = None
    direccion: Optional[str] = None
    email: Optional[str] = None
    n_documento: Optional[str] = None
    nombres: Optional[str] = None
    telefono: Optional[str] = None
    vive: bool
    parentesco: Optional[str] = None

    class Config:
        orm_mode = True
