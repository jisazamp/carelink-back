from pydantic import BaseModel


class AuthorizedUser(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    password: str
