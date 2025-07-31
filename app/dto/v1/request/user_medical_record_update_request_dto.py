from datetime import date
from pydantic import BaseModel
from typing import Optional


class UpdateUserMedicalRecordRequestDTO(BaseModel):
    alcoholismo: Optional[str] = None
    alergico_medicamento: Optional[bool] = None
    altura: Optional[int] = None
    apariencia_personal: Optional[str] = None
    cafeina: Optional[str] = None
    cirugias: Optional[str] = None
    comunicacion_no_verbal: Optional[str] = None
    comunicacion_verbal: Optional[str] = None
    continencia: Optional[str] = None
    cuidado_personal: Optional[str] = None
    discapacidades: Optional[str] = None
    id_profesional: Optional[int] = None
    limitaciones: Optional[str] = None
    emer_medica: Optional[str] = None
    eps: Optional[str] = None
    estado_de_animo: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    frecuencia_cardiaca: Optional[float] = None
    historial_cirugias: Optional[str] = None
    maltratado: Optional[str] = None
    maltrato: Optional[str] = None
    medicamentos_alergia: Optional[str] = None
    motivo_ingreso: Optional[str] = None
    observ_dietaespecial: Optional[str] = None
    observa_otrasalergias: Optional[str] = None
    observaciones_iniciales: Optional[str] = None
    peso: Optional[float] = None
    presion_arterial: Optional[float] = None
    sustanciaspsico: Optional[str] = None
    tabaquismo: Optional[str] = None
    telefono_emermedica: Optional[str] = None
    temperatura_corporal: Optional[float] = None
    tiene_otrasalergias: Optional[bool] = None
    dieta_especial: Optional[str] = None
    tienedieta_especial: Optional[bool] = None
    tipo_alimentacion: Optional[str] = None
    tipo_de_movilidad: Optional[str] = None
    tipo_de_sueno: Optional[str] = None
    tipo_sangre: Optional[str] = None
    diagnosticos: Optional[str] = None
    porte_clinico: Optional[str] = None
    url_hc_adjunto: Optional[str] = None  # URL del archivo adjunto en S3
