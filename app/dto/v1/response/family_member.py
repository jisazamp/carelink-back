from pydantic import BaseModel


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

    class Config:
        orm_mode = True
