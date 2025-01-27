from app.models.authorized_users import AuthorizedUsers
from app.models.family_members_by_user import FamiliaresYAcudientesPorUsuario
from app.models.family_member import FamilyMember
from app.exceptions.exceptions_classes import BusinessLogicError, EntityNotFoundError
from app.models.user import User
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload
from typing import List, Tuple
from app.security.jwt_utilities import hash_password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CareLinkCrud:
    def __init__(self, carelink_db: Session) -> None:
        self.__carelink_session = carelink_db

    def list_users(self) -> List[User]:
        return self._get_users()

    def list_user_by_user_id(self, user_id: int) -> User:
        return self._get_user_by_id(user_id)

    def list_family_members(self) -> List[FamilyMember]:
        return self._get_family_members()

    def list_family_member_by_id(self, id: int) -> FamilyMember:
        return self._get_family_member_by_id(id)

    def save_user(self, user: User) -> User:
        user.is_deleted = False
        self.__carelink_session.add(user)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(user)
        return user

    def save_family_member(self, id: int, kinship, family_member: FamilyMember):
        with self.__carelink_session.begin_nested() as transaction:
            try:
                self._get_user_by_id(id)
                kinship_string = kinship.dict()["parentezco"]
                self.__carelink_session.add(family_member)
                self.__carelink_session.flush()
                associate_family = FamiliaresYAcudientesPorUsuario(
                    **{
                        "id_usuario": id,
                        "id_acudiente": family_member.id_acudiente,
                        "parentesco": kinship_string,
                    }
                )
                self.__carelink_session.add(associate_family)
                self.__carelink_session.commit()

            except Exception as e:
                transaction.rollback()
                raise BusinessLogicError("Something went wrong")

    def _update_user(self, user: User, db_user: User) -> User:
        for key, value in user.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_user, key):
                    setattr(db_user, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_user)
        return db_user

    def _update_family_member(
        self, family_member: FamilyMember, db_family_member: FamilyMember
    ) -> FamilyMember:
        for key, value in family_member.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_family_member, key):
                    setattr(db_family_member, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_family_member)
        return db_family_member

    def update_user(self, user_id: int, user: User) -> User:
        db_user = self._get_user_by_id(user_id)
        updated_user = self._update_user(user, db_user)
        return updated_user

    def update_family_member(
        self, family_member_id: int, family_member: FamilyMember
    ) -> FamilyMember:
        db_family_member, _ = self._get_family_member_by_id(family_member_id)
        updated_family_member = self._update_family_member(
            family_member, db_family_member
        )
        return updated_family_member

    def delete_user(self, user_id: int):
        db_user = self._get_user_by_id(user_id)
        db_user.is_deleted = True
        self.__carelink_session.commit()

    def delete_family_member(self, id: int):
        db_family_member, _ = self._get_family_member_by_id(id)
        db_family_member.is_deleted = True
        self.__carelink_session.commit()

    def authenticate_user(self, email: str, password: str) -> AuthorizedUsers | None:
        user = (
            self.__carelink_session.query(AuthorizedUsers)
            .filter(AuthorizedUsers.email == email)
            .first()
        )
        if user and pwd_context.verify(password, user.password):
            return user
        return None

    def create_user(self, user_data: AuthorizedUsers) -> AuthorizedUsers:
        self.__carelink_session.add(user_data)
        self.__carelink_session.commit()
        return user_data

    def _get_users(self) -> List[User]:
        users = (
            self.__carelink_session.query(User).filter(User.is_deleted == False).all()
        )
        return users

    def _get_user_by_id(self, user_id: int) -> User:
        user = (
            self.__carelink_session.query(User)
            .filter(User.id_usuario == user_id)
            .first()
        )
        if user is None:
            raise EntityNotFoundError(f"El usuario con id {user_id} no existe")
        return user

    def _get_authorized_user_info(self, user_id) -> AuthorizedUsers:
        user = (
            self.__carelink_session.query(AuthorizedUsers)
            .filter(AuthorizedUsers.id == user_id)
            .first()
        )
        if user is None:
            raise EntityNotFoundError(f"No user found with id {user_id}")
        return user

    def _get_family_members_by_user_id(
        self, user_id: int
    ) -> List[FamiliaresYAcudientesPorUsuario]:
        family_members = (
            self.__carelink_session.query(FamiliaresYAcudientesPorUsuario)
            .join(
                FamilyMember,
                FamiliaresYAcudientesPorUsuario.id_acudiente == FamilyMember.id_acudiente,
            )
            .filter(
                FamiliaresYAcudientesPorUsuario.id_usuario == user_id,
                FamilyMember.is_deleted == False
            )
            .all()
        )
        return family_members

    def _get_family_members(self) -> List[FamilyMember]:
        return self.__carelink_session.query(FamilyMember).all()

    def _get_family_member_by_id(self, id: int) -> Tuple[FamilyMember, str]:
        family_member, parentesco = (
            self.__carelink_session.query(
                FamilyMember, FamiliaresYAcudientesPorUsuario.parentesco
            )
            .join(
                FamiliaresYAcudientesPorUsuario,
                FamilyMember.id_acudiente
                == FamiliaresYAcudientesPorUsuario.id_acudiente,
            )
            .filter(FamilyMember.id_acudiente == id)
            .first()
        )
        if family_member is None:
            raise EntityNotFoundError(f"Acudiente con id {id} no existe")
        return family_member, parentesco
