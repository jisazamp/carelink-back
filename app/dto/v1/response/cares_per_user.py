from pydantic import BaseModel


class CaresPerUserResponseDTO(BaseModel):
    id: int
    diagnostico: str
    frecuencia: str
    intervencion: str


class CaresPerUserUpdateDTO(BaseModel):
    diagnostico: str | None
    frecuencia: str | None
    intervencion: str | None
