from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, time

class CronogramaTransporteResponse(BaseModel):
    id_transporte: int
    id_cronograma_paciente: int
    direccion_recogida: Optional[str] = None
    direccion_entrega: Optional[str] = None
    hora_recogida: Optional[str] = None
    hora_entrega: Optional[str] = None
    estado: str
    observaciones: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        orm_mode = True

    @validator("hora_recogida", "hora_entrega", pre=True)
    def time_to_str(cls, v):
        if isinstance(v, time):
            return v.strftime("%H:%M:%S")
        return v

class RutaTransporteResponse(BaseModel):
    id_transporte: int
    id_cronograma_paciente: int
    nombres: str
    apellidos: str
    n_documento: str
    direccion_recogida: Optional[str] = None
    direccion_entrega: Optional[str] = None
    hora_recogida: Optional[str] = None
    hora_entrega: Optional[str] = None
    estado: str
    observaciones: Optional[str] = None

    class Config:
        orm_mode = True

class RutaDiariaResponse(BaseModel):
    fecha: str
    total_pacientes: int
    total_pendientes: int
    total_realizados: int
    total_cancelados: int
    rutas: List[RutaTransporteResponse]

    class Config:
        orm_mode = True

class TransporteResponse(BaseModel):
    success: bool = True
    message: str = "Operación exitosa"
    data: CronogramaTransporteResponse

    class Config:
        orm_mode = True

class RutaDiariaResponseWrapper(BaseModel):
    success: bool = True
    message: str = "Ruta obtenida exitosamente"
    data: RutaDiariaResponse

    class Config:
        orm_mode = True 