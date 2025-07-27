from pydantic import BaseModel
from datetime import date


class CreateUserMedicalRecordCreateRequestDTO(BaseModel):
    Tiene_OtrasAlergias: bool
    Tienedieta_especial: bool
    alcoholismo: str | None
    alergico_medicamento: bool
    altura: int
    apariencia_personal: str
    cafeina: str | None
    cirugias: str
    comunicacion_no_verbal: str
    comunicacion_verbal: str
    continencia: str | None
    cuidado_personal: str | None
    dieta_especial: str
    discapacidades: str
    emer_medica: str
    eps: str
    estado_de_animo: str | None
    fecha_ingreso: date
    frecuencia_cardiaca: float
    historial_cirugias: str
    id_usuario: int
    id_profesional: int | None
    limitaciones: str
    maltratado: str
    maltrato: str
    medicamentos_alergia: str
    motivo_ingreso: str
    observ_dietaEspecial: str
    observ_otrasalergias: str
    observaciones_iniciales: str
    otras_alergias: str
    peso: float
    presion_arterial: float
    sustanciaspsico: str | None
    tabaquismo: str
    telefono_emermedica: str
    temperatura_corporal: float
    tipo_alimentacion: str
    tipo_de_movilidad: str
    tipo_de_sueno: str
    tipo_sangre: str
    diagnosticos: str
    porte_clinico: str | None = None


class CreateUserAssociatedMedicinesRequestDTO(BaseModel):
    medicamento: str
    periodicidad: str
    observaciones: str


class CreateUserAssociatedCaresRequestDTO(BaseModel):
    diagnostico: str
    frecuencia: str
    intervencion: str


class CreateUserAssociatedInterventionsRequestDTO(BaseModel):
    diagnostico: str
    frecuencia: str
    intervencion: str


class CreateUserAssociatedVaccinesRequestDTO(BaseModel):
    efectos_secundarios: str | None
    fecha_administracion: date | None
    fecha_proxima: date | None
    vacuna: str
