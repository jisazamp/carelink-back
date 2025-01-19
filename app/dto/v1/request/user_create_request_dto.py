from pydantic import BaseModel

class AuthorizedUserCreateRequestDTO(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
