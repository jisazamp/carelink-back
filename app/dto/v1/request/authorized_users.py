from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    profesional = "profesional"
    transporte = "transporte"


class ProfessionEnum(str, Enum):
    medico = "Médico"
    enfermero = "Enfermero"
    nutricionista = "Nutricionista"
    psicologo = "Psicólogo"
    fisioterapeuta = "Fisioterapeuta"


class SpecialtyEnum(str, Enum):
    cardiologia = "Cardiología"
    pediatria = "Pediatría"
    nutricion = "Nutrición"
    psicologia_clinica = "Psicología Clínica"
    fisioterapia = "Fisioterapia"


class ChargeEnum(str, Enum):
    jefe_departamento = "Jefe de Departamento"
    especialista = "Especialista"
    residente = "Residente"


class AuthorizedUserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: RoleEnum
    password: Optional[str]


class AuthorizedUserUpdateDTO(BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]
    role: Optional[RoleEnum]

    document_number: Optional[str]
    professional_id: Optional[str]
    birthdate: Optional[date]
    entry_date: Optional[date]
    profession: Optional[ProfessionEnum]
    specialty: Optional[SpecialtyEnum]
    charge: Optional[ChargeEnum]
    phone: Optional[str]
    address: Optional[str]


class AuthorizedUserUpdate(AuthorizedUserBase):
    document_number: Optional[str]
    professional_id_number: Optional[str]
    birthdate: Optional[date]
    entry_date: Optional[date]
    profession: Optional[ProfessionEnum]
    specialty: Optional[SpecialtyEnum]
    charge: Optional[ChargeEnum]
    phone_number: Optional[str]
    home_address: Optional[str]
