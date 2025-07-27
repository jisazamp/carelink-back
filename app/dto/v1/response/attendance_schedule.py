from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class EstadoAsistenciaEnum(str, Enum):
    PENDIENTE = "PENDIENTE"
    ASISTIO = "ASISTIO"
    NO_ASISTIO = "NO_ASISTIO"
    CANCELADO = "CANCELADO"
    REAGENDADO = "REAGENDADO"


class PacientePorFechaDTO(BaseModel):
    id_cronograma_paciente: int
    id_usuario: int
    id_contrato: Optional[int]
    estado_asistencia: EstadoAsistenciaEnum
    requiere_transporte: bool
    observaciones: Optional[str]
    nombres: str
    apellidos: str
    n_documento: str
    # Información de transporte si existe
    transporte_info: Optional[dict] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    class Config:
        orm_mode = True


class CronogramaAsistenciaResponseDTO(BaseModel):
    id_cronograma: int
    id_profesional: int
    fecha: date
    comentario: Optional[str]
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    pacientes: List[PacientePorFechaDTO]

    class Config:
        orm_mode = True


class CronogramaAsistenciaPacienteResponseDTO(BaseModel):
    id_cronograma_paciente: int
    id_cronograma: int
    id_usuario: int
    id_contrato: Optional[int]
    estado_asistencia: EstadoAsistenciaEnum
    requiere_transporte: bool
    observaciones: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    # Información de transporte si existe
    transporte_info: Optional[dict] = None

    class Config:
        orm_mode = True


class AsistenciaDiariaResponseDTO(BaseModel):
    id_cronograma_paciente: int
    id_usuario: int
    nombres: str
    apellidos: str
    tipo_servicio: str
    estado_asistencia: EstadoAsistenciaEnum
    estado_texto: str
    color_estado: str
    requiere_transporte: bool
    observaciones: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    class Config:
        orm_mode = True 