from pydantic import BaseModel
from app.dto.v1.response.family_member import FamilyMemberResponseDTO


class FamilyMembersByUserResponseDTO(BaseModel):
    id_acudiente: int
    id_usuario: int
    acudiente: FamilyMemberResponseDTO
    parentesco: str

    class Config:
        orm_mode=True
