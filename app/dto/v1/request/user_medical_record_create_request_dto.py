from pydantic import BaseModel


class CreateUserMedicalRecordCreateRequestDTO(BaseModel):
    alcoholismo: bool
    alergico_medicamento: bool
    altura: int
    cafeina: bool
    cirugias: bool
    discapacidad: bool
    emer_medica: str
    historial_cirugias: str
    id_usuario: int
    maltratado: bool
    medicamentos_alergia: str
    motivo_ingreso: str
    observ_dietaEspecial: str
    observ_otrasalergias: str
    sustanciaspsico: bool
    tabaquismo: bool
    telefono_emermedica: str
    Tiene_OtrasAlergias: bool
    Tienedieta_especial: bool
    tipo_sangre: str
