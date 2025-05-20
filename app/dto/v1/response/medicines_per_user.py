from pydantic import BaseModel


class MedicinesPerUserResponseDTO(BaseModel):
    id: int
    medicamento: str | None
    periodicidad: str | None
    observaciones: str | None


class MedicinesPerUserUpdateDTO(BaseModel):
    medicamento: str | None
    periodicidad: str | None
    observaciones: str | None
