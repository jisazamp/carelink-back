from datetime import date
from pydantic import BaseModel
from typing import Optional


class UpdateUserMedicalRecordRequestDTO(BaseModel):
    alcoholismo: Optional[bool] = None
    alergico_medicamento: Optional[bool] = None
    altura: Optional[int] = None
    cafeina: Optional[bool] = None
    cirugias: Optional[bool] = None
    discapacidad: Optional[bool] = None
    emer_medica: Optional[str] = None
    eps: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    frecuencia_cardiaca: Optional[float] = None
    historial_cirugias: Optional[str] = None
    maltratado: Optional[bool] = None
    medicamentos_alergia: Optional[str] = None
    motivo_ingreso: Optional[str] = None
    observ_dietaespecial: Optional[str] = None
    observa_otrasalergias: Optional[str] = None
    observaciones_iniciales: Optional[str] = None
    peso: Optional[float] = None
    presion_arterial: Optional[float] = None
    sustanciaspsico: Optional[bool] = None
    tabaquismo: Optional[bool] = None
    telefono_emermedica: Optional[str] = None
    temperatura_corporal: Optional[float] = None
    tiene_otrasalergias: Optional[bool] = None
    tienedieta_especial: Optional[bool] = None
    tipo_sangre: Optional[str] = None
