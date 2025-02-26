from datetime import date
from pydantic import BaseModel


class CreateUserMedicalRecordResponseDTO(BaseModel):
    alcoholismo: bool
    alergico_medicamento: bool
    altura: int
    cafeina: bool
    cirugias: bool
    discapacidad: bool
    emer_medica: str
    eps: str
    fecha_ingreso: date
    frecuencia_cardiaca: float
    historial_cirugias: str
    id_usuario: int
    maltratado: bool
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
    Tiene_OtrasAlergias: bool
    Tienedieta_especial: bool
    tipo_sangre: str
