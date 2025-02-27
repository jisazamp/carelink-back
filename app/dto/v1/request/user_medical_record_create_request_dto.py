from pydantic import BaseModel
from datetime import date


class CreateUserMedicalRecordCreateRequestDTO(BaseModel):
    Tiene_OtrasAlergias: bool
    Tienedieta_especial: bool
    alcoholismo: bool
    alergico_medicamento: bool
    altura: int
    apariencia_personal: str
    cafeina: bool
    cirugias: bool
    comunicacion_no_verbal: str
    comunicacion_verbal: str
    continencia: bool
    cuidado_personal: str
    discapacidad: bool
    emer_medica: str
    eps: str
    estado_de_animo: str
    fecha_ingreso: date
    frecuencia_cardiaca: float
    historial_cirugias: str
    id_usuario: int
    maltratado: bool
    maltrato: bool
    medicamentos_alergia: str
    motivo_ingreso: str
    observ_dietaEspecial: str
    observ_otrasalergias: str
    observaciones_iniciales: str
    peso: float
    presion_arterial: float
    sustanciaspsico: bool
    tabaquismo: bool
    telefono_emermedica: str
    temperatura_corporal: float
    tipo_alimentacion: str
    tipo_de_movilidad: str
    tipo_de_sueno: str
    tipo_sangre: str
