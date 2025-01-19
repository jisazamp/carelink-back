import os
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.exceptions.exceptions_classes import EntityNotFoundError

BASE_URL = os.getenv("BASE_URL")


class CareLinkCrud:
    def __init__(self, carelink_db: Session) -> None:
        self.__carelink_session = carelink_db

    def list_users(self) -> List[User]:
        return self._get_users()

    def list_user_by_user_id(self, user_id: int) -> User:
        return self._get_user_by_id(user_id)

    def save_user(self, user: User) -> User:
        self.__carelink_session.add(user)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(user)
        return user

    def _update_user(self, user: User, db_user: User) -> User:
        for key, value in user.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_user, key):
                    setattr(db_user, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user: User) -> User:
        db_user = self._get_user_by_id(user_id)
        updated_user = self._update_user(user, db_user)
        return updated_user

    def delete_user(self, user_id) -> User:
        db_user = self._get_user_by_id(user_id)
        self.__carelink_session.delete(db_user)
        self.__carelink_session.commit()

    def _get_users(self) -> List[User]:
        users = self.__carelink_session.query(User).all()
        if not users:
            raise EntityNotFoundError("No users found on database")
        return users

    def _get_user_by_id(self, user_id: int) -> User:
        user = (
            self.__carelink_session.query(User)
            .filter(User.id_usuario == user_id)
            .first()
        )
        if user is None:
            raise EntityNotFoundError(f"No user found with id {user_id}")
        return user
