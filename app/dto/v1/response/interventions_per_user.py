from pydantic import BaseModel


class InterventionsPerUserResponseDTO(BaseModel):
    id: int
    diagnostico: str
    frecuencia: str
    intervencion: str


class InterventionsPerUserUpdateDTO(BaseModel):
    diagnostico: str | None
    frecuencia: str | None
    intervencion: str | None
