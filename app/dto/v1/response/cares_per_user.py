from pydantic import BaseModel


class CaresPerUserResponseDTO(BaseModel):
    id: int
    diagnostico: str
    frecuencia: str
    intervencion: str
