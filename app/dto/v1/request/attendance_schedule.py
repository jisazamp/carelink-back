from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class EstadoAsistenciaEnum(str, Enum):
    PENDIENTE = "PENDIENTE"
    ASISTIO = "ASISTIO"
    NO_ASISTIO = "NO_ASISTIO"
    CANCELADO = "CANCELADO"
    REAGENDADO = "REAGENDADO"

class CronogramaAsistenciaCreateDTO(BaseModel):
    id_profesional: int = Field(..., description="ID del profesional")
    fecha: date = Field(..., description="Fecha del cronograma")
    comentario: Optional[str] = Field(None, description="Comentario opcional")

class CronogramaAsistenciaPacienteCreateDTO(BaseModel):
    id_cronograma: int = Field(..., description="ID del cronograma")
    id_usuario: int = Field(..., description="ID del usuario/paciente")
    id_contrato: Optional[int] = Field(None, description="ID del contrato (opcional)")
    estado_asistencia: EstadoAsistenciaEnum = Field(EstadoAsistenciaEnum.PENDIENTE, description="Estado de asistencia")
    requiere_transporte: bool = Field(False, description="Si requiere transporte")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")

class CronogramaAsistenciaUpdateDTO(BaseModel):
    comentario: Optional[str] = Field(None, description="Comentario opcional")

class EstadoAsistenciaUpdateDTO(BaseModel):
    estado_asistencia: EstadoAsistenciaEnum = Field(..., description="Nuevo estado de asistencia")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    nueva_fecha: Optional[date] = Field(None, description="Nueva fecha para reagendamiento")

class ReagendarPacienteDTO(BaseModel):
    id_cronograma_paciente: int = Field(..., description="ID del cronograma del paciente")
    nueva_fecha: date = Field(..., description="Nueva fecha para reagendamiento")
    observaciones: Optional[str] = Field(None, description="Observaciones del reagendamiento") 