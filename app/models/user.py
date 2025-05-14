from .base import Base
from sqlalchemy import Boolean, Column, Integer, String, Date, DateTime


class User(Base):
    __tablename__ = "Usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    apellidos = Column(String(50))
    direccion = Column(String)
    email = Column(String)
    escribe = Column(Boolean)
    estado = Column(String)
    estado_civil = Column(String)
    fecha_nacimiento = Column(Date)
    fecha_registro = Column(DateTime)
    genero = Column(String)
    grado_escolaridad = Column(String)
    ha_estado_en_otro_centro = Column(Boolean)
    lee = Column(Boolean)
    lugar_nacimiento = Column(String)
    lugar_procedencia = Column(String)
    n_documento = Column(String(255))
    nombres = Column(String(50))
    nucleo_familiar = Column(String)
    ocupacion_quedesempeño = Column(String)
    origen_otrocentro = Column(String)
    proteccion_exequial = Column(Boolean)
    regimen_seguridad_social = Column(String)
    telefono = Column(String)
    tipo_afiliacion = Column(String)
    url_imagen = Column(String)
    is_deleted = Column(Boolean)
    profesion = Column(String)

    class Config:
        orm_mode = True
