from pydantic import BaseModel


class CreateFamilyMemberRequestDTO(BaseModel):
    acudiente: bool
    apellidos: str
    direccion: str
    email: str
    is_deleted: bool
    n_documento: str
    nombres: str
    telefono: str
    vive: bool


class AssociateFamilyMemberRequestDTO(BaseModel):
    parentezco: str


class UpdateFamilyMemberRequestDTO(BaseModel):
    acudiente: bool | None
    apellidos: str | None
    direccion: str | None
    email: str | None
    n_documento: str | None
    nombres: str | None
    telefono: str | None
    vive: bool | None
