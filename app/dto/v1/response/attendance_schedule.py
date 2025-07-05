from datetime import date
from pydantic import BaseModel
from typing import List, Optional


class PacientePorFechaDTO(BaseModel):
    id_cronograma_paciente: int
    id_usuario: int
    id_contrato: int
    estado_asistencia: str
    nombres: str
    apellidos: str
    n_documento: str

    class Config:
        orm_mode = True


class CronogramaAsistenciaResponseDTO(BaseModel):
    id_cronograma: int
    id_profesional: int
    fecha: date
    comentario: Optional[str]
    pacientes: List[PacientePorFechaDTO]

    class Config:
        orm_mode = True


class CronogramaAsistenciaPacienteResponseDTO(BaseModel):
    id_cronograma_paciente: int
    id_cronograma: int
    id_usuario: int
    id_contrato: int
    estado_asistencia: str
    observaciones: Optional[str] = None

    class Config:
        orm_mode = True 