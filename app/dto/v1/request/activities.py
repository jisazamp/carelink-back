from datetime import date
from pydantic import BaseModel
from typing import Optional


class ActividadesGrupalesCreate(BaseModel):
    id_profesional: Optional[int] = None
    id_tipo_actividad: Optional[int] = None
    comentarios: Optional[str] = None
    descripcion: Optional[str] = None
    duracion: Optional[int] = None
    fecha: Optional[date] = None
    nombre: Optional[str] = None


class ActividadesGrupalesUpdate(BaseModel):
    id_profesional: Optional[int] = None
    id_tipo_actividad: Optional[int] = None
    comentarios: Optional[str] = None
    descripcion: Optional[str] = None
    duracion: Optional[int] = None
    fecha: Optional[date] = None
    nombre: Optional[str] = None
