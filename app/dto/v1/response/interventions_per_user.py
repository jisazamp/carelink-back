from pydantic import BaseModel


class InterventionsPerUserResponseDTO(BaseModel):
    id: int
    diagnostico: str
    frecuencia: str
    intervencion: str
