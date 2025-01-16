import os
from sqlalchemy.orm import Session

BASE_URL = os.getenv("BASE_URL")


class CareLinkCrud:
    def __init__(self, carelink_db: Session) -> None:
        self.__carelink_session = carelink_db
