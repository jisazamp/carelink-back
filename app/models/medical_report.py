from .base import Base
from .professional import Profesionales
from sqlalchemy import Column, Integer, Text, Float, Enum, ForeignKey, Date
from sqlalchemy.orm import relationship


class ReportesClinicos(Base):
    __tablename__ = "ReportesClinicos"

    id_reporteclinico = Column(Integer, primary_key=True, autoincrement=True)
    id_historiaclinica = Column(
        Integer, ForeignKey("HistoriaClinica.id_historiaclinica"), nullable=False
    )
    id_profesional = Column(
        Integer, ForeignKey(Profesionales.id_profesional), nullable=False
    )
    IMC = Column(Float)
    Obs_habitosalimenticios = Column(Text)
    Porc_grasacorporal = Column(Float)
    Porc_masamuscular = Column(Float)
    area_afectiva = Column(Text)
    area_comportamental = Column(Text)
    areacognitiva = Column(Text)
    areainterpersonal = Column(Text)
    areasomatica = Column(Text)
    circunferencia_cadera = Column(Float)
    circunferencia_cintura = Column(Float)
    consumo_aguadiaria = Column(Float)
    diagnostico = Column(Text)
    fecha_registro = Column(Date)
    frecuencia_cardiaca = Column(Integer)
    frecuencia_respiratoria = Column(Integer)
    motivo_consulta = Column(Text)
    nivel_dolor = Column(Integer)
    observaciones = Column(Text)
    peso = Column(Integer)
    presion_arterial = Column(Integer)
    pruebas_examenes = Column(Text)
    recomendaciones = Column(Text)
    remision = Column(Text)
    saturacionOxigeno = Column(Integer)
    temperatura_corporal = Column(Float)
    tipo_reporte = Column(Text)
    frecuencia_actividadfisica = Column(
        Enum("Baja", "Moderada", "Alta", name="frecuencia_actividadfisica")
    )

    profesional = relationship(
        "Profesionales", foreign_keys=[id_profesional], lazy="joined"
    )
