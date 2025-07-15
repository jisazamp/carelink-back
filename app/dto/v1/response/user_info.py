from pydantic import BaseModel


class UserInfo(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
