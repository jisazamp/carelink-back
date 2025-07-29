from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

from app.dto.v1.request.authorized_users import (
    ChargeEnum,
    ProfessionEnum,
    RoleEnum,
    SpecialtyEnum,
)


class ProfessionalUserDTO(BaseModel):
    birthdate: date
    charge: ChargeEnum
    document_number: str
    email: str
    entry_date: date
    first_name: str
    home_address: str
    last_name: str
    phone_number: str
    profession: ProfessionEnum
    professional_id_number: str
    specialty: SpecialtyEnum


class AuthorizedUserCreateRequestDTO(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    role: RoleEnum
    professional_user: Optional[ProfessionalUserDTO] = Field(default=None)
