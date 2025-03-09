from datetime import date, datetime
from pydantic import BaseModel


class UserCreateRequestDTO(BaseModel):
    apellidos: str
    direccion: str | None = None
    email: str | None = None
    escribe: bool
    estado: str | None = None
    estado_civil: str | None = None
    fecha_nacimiento: date
    fecha_registro: datetime
    genero: str | None = None
    grado_escolaridad: str | None = None
    ha_estado_en_otro_centro: bool
    lee: bool
    lugar_nacimiento: str | None = None
    lugar_procedencia: str | None = None
    n_documento: str | None = None
    nombres: str
    nucleo_familiar: str | None = None
    ocupacion_quedesempeño: str | None = None
    origen_otrocentro: str | None = None
    proteccion_exequial: bool
    regimen_seguridad_social: str | None = None
    telefono: int | None = None
    tipo_afiliacion: str | None = None
    url_imagen: str | None = None
