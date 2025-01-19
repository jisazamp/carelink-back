from pydantic import BaseModel

class UserCreateRequestDTO(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
