from pydantic import BaseModel


class UserResponseDTO(BaseModel):
    nombres: str
    apellidos: str

    class Config:
        orm_mode = True
        from_attributes=True
