from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date


class ActivityUserDTO(BaseModel):
    id: int
    id_usuario: int
    id_actividad: int
    fecha_asignacion: datetime
    estado_participacion: str
    observaciones: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    # Información del usuario
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    n_documento: Optional[str] = None
    
    class Config:
        orm_mode = True


class ActivityWithUsersDTO(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    fecha: Optional[date] = None
    duracion: Optional[int] = None
    comentarios: Optional[str] = None
    id_profesional: Optional[int] = None
    id_tipo_actividad: Optional[int] = None
    
    # Información del profesional
    profesional_nombres: Optional[str] = None
    profesional_apellidos: Optional[str] = None
    
    # Información del tipo de actividad
    tipo_actividad: Optional[str] = None
    
    # Usuarios asignados
    usuarios_asignados: List[ActivityUserDTO] = []
    total_usuarios: int = 0
    
    class Config:
        orm_mode = True


class UserForActivityDTO(BaseModel):
    id_usuario: int
    nombres: str
    apellidos: str
    n_documento: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    estado: Optional[str] = None
    
    # Información del cronograma
    tiene_cronograma_fecha: bool = False
    estado_asistencia: Optional[str] = None
    
    class Config:
        orm_mode = True


class AssignUsersToActivityDTO(BaseModel):
    id_actividad: Optional[int] = None  # Opcional porque viene en la URL
    usuarios_ids: List[int]
    estado_participacion: str = "PENDIENTE"
    observaciones: Optional[str] = None


class UpdateUserActivityStatusDTO(BaseModel):
    estado_participacion: str
    observaciones: Optional[str] = None 