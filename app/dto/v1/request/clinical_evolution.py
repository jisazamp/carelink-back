from datetime import date
from pydantic import BaseModel
from typing import Optional


class ClinicalEvolutionCreate(BaseModel):
    id_profesional: int
    id_reporteclinico: int
    fecha_evolucion: Optional[date] = None
    observacion_evolucion: Optional[str] = None
    tipo_report: Optional[str] = None


class ClinicalEvolutionUpdate(BaseModel):
    id_profesional: int
    id_reporteclinico: int
    fecha_evolucion: Optional[date] = None
    observacion_evolucion: Optional[str] = None
    tipo_report: Optional[str] = None
