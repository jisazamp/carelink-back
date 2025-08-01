from pydantic import BaseModel


class AuthorizedUser(BaseModel):
    id: int
    email: str
    first_name: str
    is_deleted: bool
    last_name: str
    role: str

    class Config:
        orm_mode = True
