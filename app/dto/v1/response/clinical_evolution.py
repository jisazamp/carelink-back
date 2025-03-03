from datetime import date
from pydantic import BaseModel

from app.dto.v1.response.professional import ProfessionalResponse


class ClinicalEvolutionResponse(BaseModel):
    id_TipoReporte: int
    id_reporteclinico: int
    id_profesional: int
    fecha_evolucion: date
    observacion_evolucion: str
    tipo_report: str
    profesional: ProfessionalResponse | None

    class Config:
        orm_mode = True
