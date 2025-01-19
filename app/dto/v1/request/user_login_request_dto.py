from pydantic import BaseModel


class UserLoginRequestDTO(BaseModel):
    email: str
    password: str
