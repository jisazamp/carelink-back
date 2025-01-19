from datetime import date, datetime
from pydantic import BaseModel


class UserResponseDTO(BaseModel):
    apellidos: str
    direccion: str | None
    email: str | None
    escribe: bool
    estado: str
    estado_civil: str | None
    fecha_nacimiento: date | None
    fecha_registro: datetime
    genero: str | None
    grado_escolaridad: str | None
    ha_estado_en_otro_centro: bool
    id_usuario: int
    lee: bool
    lugar_nacimiento: str | None
    lugar_procedencia: str | None
    n_documento: str | None
    nombres: str
    nucleo_familiar: str | None
    ocupacion_quedesempeño: str | None
    origen_otrocentro: str | None
    proteccion_exequial: bool
    regimen_seguridad_social: str | None
    telefono: str | None
    tipo_afiliacion: str | None


class UserUpdateRequestDTO(BaseModel):
    apellidos: str | None
    direccion: str | None
    email: str | None
    escribe: bool | None
    estado: str | None
    estado_civil: str | None
    fecha_nacimiento: date | None
    fecha_registro: datetime | None
    genero: str | None
    grado_escolaridad: str | None
    ha_estado_en_otro_centro: bool | None
    id_usuario: int | None
    lee: bool | None
    lugar_nacimiento: str | None
    lugar_procedencia: str | None
    n_documento: str | None
    nombres: str | None
    nucleo_familiar: str | None
    ocupacion_quedesempeño: str | None
    origen_otrocentro: str | None
    proteccion_exequial: bool | None
    regimen_seguridad_social: str | None
    telefono: str | None
    tipo_afiliacion: str | None
