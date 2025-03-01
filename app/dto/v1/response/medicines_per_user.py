from datetime import date
from pydantic import BaseModel


class MedicinesPerUserResponseDTO(BaseModel):
    id: int
    Fecha_inicio: date
    fecha_fin: date
    medicamento: str
    periodicidad: str
