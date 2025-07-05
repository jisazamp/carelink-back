from datetime import date
from pydantic import BaseModel
from typing import List, Optional

class CronogramaAsistenciaCreateDTO(BaseModel):
    id_profesional: int
    fecha: date
    comentario: Optional[str] = None

class CronogramaAsistenciaPacienteCreateDTO(BaseModel):
    id_cronograma: int
    id_usuario: int
    id_contrato: int
    estado_asistencia: str = "PENDIENTE"

class CronogramaAsistenciaUpdateDTO(BaseModel):
    comentario: Optional[str] = None

class EstadoAsistenciaUpdateDTO(BaseModel):
    estado_asistencia: str

class ReagendarPacienteDTO(BaseModel):
    id_cronograma_paciente: int
    nueva_fecha: date 