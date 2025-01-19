from pydantic import BaseModel


class CreateUserResponseDTO(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    token: str
