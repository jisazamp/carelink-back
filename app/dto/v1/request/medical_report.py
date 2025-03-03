from datetime import date
from pydantic import BaseModel
from typing import Optional


class ReporteClinicoCreate(BaseModel):
    id_historiaclinica: int
    id_profesional: int
    IMC: Optional[float] = None
    Obs_habitosalimenticios: Optional[str] = None
    Porc_grasacorporal: Optional[float] = None
    Porc_masamuscular: Optional[float] = None
    area_afectiva: Optional[str] = None
    area_comportamental: Optional[str] = None
    areacognitiva: Optional[str] = None
    areainterpersonal: Optional[str] = None
    areasomatica: Optional[str] = None
    circunferencia_cadera: Optional[float] = None
    circunferencia_cintura: Optional[float] = None
    consumo_aguadiaria: Optional[float] = None
    diagnostico: Optional[str] = None
    fecha_registro: Optional[date] = None
    frecuencia_actividadfisica: Optional[str] = None
    frecuencia_cardiaca: Optional[int] = None
    frecuencia_respiratoria: Optional[int] = None
    motivo_consulta: Optional[str] = None
    nivel_dolor: Optional[int] = None
    observaciones: Optional[str] = None
    peso: Optional[int] = None
    presion_arterial: Optional[int] = None
    pruebas_examenes: Optional[str] = None
    recomendaciones: Optional[str] = None
    remision: Optional[str] = None
    saturacionOxigeno: Optional[int] = None
    temperatura_corporal: Optional[float] = None
    tipo_reporte: Optional[str] = None


class ReporteClinicoUpdate(BaseModel):
    IMC: Optional[float] = None
    Obs_habitosalimenticios: Optional[str] = None
    Porc_grasacorporal: Optional[float] = None
    Porc_masamuscular: Optional[float] = None
    area_afectiva: Optional[str] = None
    area_comportamental: Optional[str] = None
    areacognitiva: Optional[str] = None
    areainterpersonal: Optional[str] = None
    areasomatica: Optional[str] = None
    circunferencia_cadera: Optional[float] = None
    circunferencia_cintura: Optional[float] = None
    consumo_aguadiaria: Optional[float] = None
    diagnostico: Optional[str] = None
    fecha_registro: Optional[date] = None
    frecuencia_actividadfisica: Optional[str] = None
    frecuencia_cardiaca: Optional[int] = None
    frecuencia_respiratoria: Optional[int] = None
    motivo_consulta: Optional[str] = None
    nivel_dolor: Optional[int] = None
    observaciones: Optional[str] = None
    peso: Optional[int] = None
    presion_arterial: Optional[int] = None
    pruebas_examenes: Optional[str] = None
    recomendaciones: Optional[str] = None
    remision: Optional[str] = None
    saturacionOxigeno: Optional[int] = None
    temperatura_corporal: Optional[float] = None
    tipo_reporte: Optional[str] = None
