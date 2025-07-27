from .base import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Date, Numeric
from .professional import Profesionales


class MedicalRecord(Base):
    __tablename__ = "HistoriaClinica"

    Tiene_OtrasAlergias = Column(Boolean, nullable=False)
    Tienedieta_especial = Column(Boolean, nullable=False)
    alcoholismo = Column(Text)
    alergico_medicamento = Column(Boolean, nullable=False)
    altura = Column(Integer, nullable=False)
    apariencia_personal = Column(String())
    cafeina = Column(Text)
    cirugias = Column(Text)
    comunicacion_no_verbal = Column(String)
    comunicacion_verbal = Column(String)
    continencia = Column(String)
    cuidado_personal = Column(String())
    dieta_especial = Column(Text)
    discapacidades = Column(Text)
    emer_medica = Column(String(30), nullable=True)
    eps = Column(Text, nullable=True)
    estado_de_animo = Column(String)
    fecha_ingreso = Column(Date, nullable=False)
    frecuencia_cardiaca = Column(Numeric, nullable=False)
    historial_cirugias = Column(Text)
    id_historiaclinica = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    id_profesional = Column(Integer, ForeignKey("Profesionales.id_profesional"), nullable=True)
    limitaciones = Column(Text)
    maltratado = Column(Text)
    maltrato = Column(Text)
    medicamentos_alergia = Column(Text)
    motivo_ingreso = Column(Text)
    observ_dietaEspecial = Column(Text)
    observ_otrasalergias = Column(Text)
    observaciones_iniciales = Column(Text)
    otras_alergias = Column(Text)
    peso = Column(Numeric, nullable=False)
    presion_arterial = Column(Numeric, nullable=False)
    sustanciaspsico = Column(Text)
    tabaquismo = Column(Text)
    telefono_emermedica = Column(String(17))
    temperatura_corporal = Column(Numeric, nullable=False)
    tipo_alimentacion = Column(String())
    tipo_de_movilidad = Column(String())
    tipo_de_sueno = Column(String())
    tipo_sangre = Column(String(3), nullable=False)  # ENUM values are max 3 chars
    diagnosticos = Column(Text)
    porte_clinico = Column(Text)  # Campo específico para visitas domiciliarias
