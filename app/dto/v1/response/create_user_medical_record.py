from datetime import date
from pydantic import BaseModel


class CreateUserMedicalRecordResponseDTO(BaseModel):
    id_historiaclinica: int | None
    Tiene_OtrasAlergias: bool | None
    Tienedieta_especial: bool | None
    alcoholismo: str | None
    alergico_medicamento: bool | None
    altura: int | None
    apariencia_personal: str | None
    cafeina: str | None
    cirugias: str | None
    comunicacion_no_verbal: str | None
    comunicacion_verbal: str | None
    continencia: str | None
    cuidado_personal: str | None
    dieta_especial: str | None
    discapacidades: str | None
    emer_medica: str | None
    eps: str | None
    estado_de_animo: str | None
    fecha_ingreso: date | None
    frecuencia_cardiaca: float | None
    historial_cirugias: str | None
    id_usuario: int | None
    id_profesional: int | None
    limitaciones: str | None
    maltratado: str | None
    maltrato: str | None
    medicamentos_alergia: str | None
    motivo_ingreso: str | None
    observ_dietaEspecial: str | None
    observ_otrasalergias: str | None
    observaciones_iniciales: str | None
    otras_alergias: str | None
    peso: float | None
    presion_arterial: float | None
    sustanciaspsico: str | None
    tabaquismo: str | None
    telefono_emermedica: str | None
    temperatura_corporal: float
    tipo_alimentacion: str | None
    tipo_de_movilidad: str | None
    tipo_de_sueno: str | None
    tipo_sangre: str | None
    diagnosticos: str
    porte_clinico: str | None = None
    url_hc_adjunto: str | None = None  # URL del archivo adjunto en S3
