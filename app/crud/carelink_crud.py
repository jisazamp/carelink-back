import os
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User

BASE_URL = os.getenv("BASE_URL")


class CareLinkCrud:
    def __init__(self, carelink_db: Session) -> None:
        self.__carelink_session = carelink_db

    def list(self) -> List[User]:
        return self.__carelink_session.query(User).all()
