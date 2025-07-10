from pydantic import BaseModel, Field
from typing import Optional
from datetime import time

class CreateTransporteRequest(BaseModel):
    id_cronograma_paciente: int = Field(..., description="ID del cronograma del paciente")
    direccion_recogida: Optional[str] = Field(None, description="Dirección de recogida")
    direccion_entrega: Optional[str] = Field(None, description="Dirección de entrega")
    hora_recogida: Optional[str] = Field(None, description="Hora de recogida (HH:MM:SS)")
    hora_entrega: Optional[str] = Field(None, description="Hora de entrega (HH:MM:SS)")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")

class UpdateTransporteRequest(BaseModel):
    direccion_recogida: Optional[str] = Field(None, description="Dirección de recogida")
    direccion_entrega: Optional[str] = Field(None, description="Dirección de entrega")
    hora_recogida: Optional[str] = Field(None, description="Hora de recogida (HH:MM:SS)")
    hora_entrega: Optional[str] = Field(None, description="Hora de entrega (HH:MM:SS)")
    estado: Optional[str] = Field(None, description="Estado del transporte")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales") 