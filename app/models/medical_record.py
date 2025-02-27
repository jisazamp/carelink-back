from .base import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Date, Numeric


class MedicalRecord(Base):
    __tablename__ = "HistoriaClinica"

    Tiene_OtrasAlergias = Column(Boolean, nullable=False)
    Tienedieta_especial = Column(Boolean, nullable=False)
    alcoholismo = Column(Boolean, nullable=False)
    alergico_medicamento = Column(Boolean, nullable=False)
    altura = Column(Integer, nullable=False)
    cafeina = Column(Boolean, nullable=False)
    cirugias = Column(Boolean, nullable=False)
    comunicacion_no_verbal = Column(String)
    comunicacion_verbal = Column(String)
    discapacidad = Column(Boolean, nullable=False)
    emer_medica = Column(Text, nullable=False)
    eps = Column(Text, nullable=True)
    estado_de_animo = Column(String)
    fecha_ingreso = Column(Date, nullable=True)
    frecuencia_cardiaca = Column(Numeric, nullable=False)
    historial_cirugias = Column(Text)
    id_historiaclinica = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    maltratado = Column(Boolean, nullable=False)
    maltrato = Column(Boolean, nullable=False)
    medicamentos_alergia = Column(Text)
    motivo_ingreso = Column(Text)
    observ_dietaEspecial = Column(Text)
    observ_otrasalergias = Column(Text)
    observaciones_iniciales = Column(Text)
    peso = Column(Numeric)
    presion_arterial = Column(Numeric)
    sustanciaspsico = Column(Boolean, nullable=False)
    tabaquismo = Column(Boolean, nullable=False)
    telefono_emermedica = Column(String(17))
    temperatura_corporal = Column(Numeric)
    tipo_sangre = Column(String(), nullable=False)
