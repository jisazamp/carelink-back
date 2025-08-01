from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class UserFlowItemDTO(BaseModel):
    id_usuario: int
    nombre_completo: str
    id_contrato: int
    visitas_mes: int


class UserFlowStatsDTO(BaseModel):
    usuarios_mes: int
    tasa_asistencia: float
    usuarios_mes_trend: float
    tasa_asistencia_trend: float


class UserFlowResponseDTO(BaseModel):
    stats: UserFlowStatsDTO
    users: List[UserFlowItemDTO] 