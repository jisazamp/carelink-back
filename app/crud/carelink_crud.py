from app.exceptions.exceptions_classes import BusinessLogicError, EntityNotFoundError
from app.models.authorized_users import AuthorizedUsers
from app.models.cares_per_user import CuidadosEnfermeriaPorUsuario
from app.models.family_member import FamilyMember
from app.models.family_members_by_user import FamiliaresYAcudientesPorUsuario
from app.models.interventions_per_user import IntervencionesPorUsuario
from app.models.medical_record import MedicalRecord
from app.models.medicines_per_user import MedicamentosPorUsuario
from app.models.user import User
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import List, Tuple

from app.models.vaccines import VacunasPorUsuario

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

    def list_user_medical_record(self, id: int) -> MedicalRecord | None:
        self._get_user_by_id(id)
        return self._get_user_medical_record_by_user_id(id)

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
                associate_family = FamiliaresYAcudientesPorUsuario(**{
                    "id_usuario": id,
                    "id_acudiente": family_member.id_acudiente,
                    "parentesco": kinship_string,
                })
                self.__carelink_session.add(associate_family)
                self.__carelink_session.commit()

            except Exception:
                transaction.rollback()
                raise BusinessLogicError("Something went wrong")

    def save_user_medical_record(
        self,
        id: int,
        record: MedicalRecord,
        medicines: List[MedicamentosPorUsuario],
        cares: List[CuidadosEnfermeriaPorUsuario],
        interventions: List[IntervencionesPorUsuario],
        vaccines: List[VacunasPorUsuario],
    ):
        with self.__carelink_session.begin_nested() as transaction:
            try:
                self._get_user_by_id(id)
                self.__carelink_session.add(record)
                self.__carelink_session.flush()
                for medicine in medicines:
                    medicine.id_historiaClinica = record.id_historiaclinica
                    self.__carelink_session.add(medicine)
                for care in cares:
                    care.id_historiaClinica = record.id_historiaclinica
                    self.__carelink_session.add(care)
                for intervention in interventions:
                    intervention.id_historiaClinica = record.id_historiaclinica
                    self.__carelink_session.add(intervention)
                for vaccine in vaccines:
                    vaccine.id_historiaClinica = record.id_historiaclinica
                    self.__carelink_session.add(vaccine)
                self.__carelink_session.commit()
            except Exception:
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

    def update_user_medical_record(
        self, user_id: int, record_id: int, update_data: dict
    ) -> MedicalRecord:
        self._get_user_by_id(user_id)

        record_to_update = (
            self.__carelink_session.query(MedicalRecord)
            .filter_by(id_historiaclinica=record_id, id_usuario=user_id)
            .first()
        )

        if not record_to_update:
            raise HTTPException(
                status_code=404,
                detail=f"Medical record with ID {record_id} not found for user {user_id}",
            )

        for key, value in update_data.items():
            setattr(record_to_update, key, value)

        self.__carelink_session.commit()
        self.__carelink_session.refresh(record_to_update)

        return record_to_update

    def delete_user(self, user_id: int):
        db_user = self._get_user_by_id(user_id)
        db_user.is_deleted = True
        self.__carelink_session.commit()

    def delete_family_member(self, id: int):
        db_family_member, _ = self._get_family_member_by_id(id)
        db_family_member.is_deleted = True
        self.__carelink_session.commit()

    def delete_user_medical_record(self, record_id: int):
        db_record = self._get_medical_record_by_id(record_id)
        self.__carelink_session.delete(db_record)
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

    def create_user_medical_record(
        self, user_id: int, record: MedicalRecord
    ) -> MedicalRecord:
        self._get_user_by_id(user_id)
        self.__carelink_session.add(record)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(record)
        return record

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
                FamiliaresYAcudientesPorUsuario.id_acudiente
                == FamilyMember.id_acudiente,
            )
            .filter(
                FamiliaresYAcudientesPorUsuario.id_usuario == user_id,
                FamilyMember.is_deleted == False,
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

    def _get_user_medical_record_by_user_id(self, id: int) -> MedicalRecord | None:
        return (
            self.__carelink_session.query(MedicalRecord)
            .filter(MedicalRecord.id_usuario == id)
            .first()
        )

    def _get_medical_record_by_id(self, id: int) -> MedicalRecord:
        record = (
            self.__carelink_session.query(MedicalRecord)
            .filter(MedicalRecord.id_historiaclinica == id)
            .first()
        )
        if not record:
            raise EntityNotFoundError("Record not found")
        return record

    def _get_user_medicines_by_medical_record_id(
        self, id: int
    ) -> List[MedicamentosPorUsuario]:
        self._get_medical_record_by_id(id)
        return (
            self.__carelink_session.query(MedicamentosPorUsuario)
            .filter(MedicamentosPorUsuario.id_historiaClinica == id)
            .all()
        )

    def _get_user_cares_by_medical_record_id(
        self, id: int
    ) -> List[CuidadosEnfermeriaPorUsuario]:
        self._get_medical_record_by_id(id)
        return (
            self.__carelink_session.query(CuidadosEnfermeriaPorUsuario)
            .filter(CuidadosEnfermeriaPorUsuario.id_historiaClinica == id)
            .all()
        )

    def _get_user_interventions_by_medical_record_id(
        self, id: int
    ) -> List[IntervencionesPorUsuario]:
        self._get_medical_record_by_id(id)
        return (
            self.__carelink_session.query(IntervencionesPorUsuario)
            .filter(IntervencionesPorUsuario.id_historiaClinica == id)
            .all()
        )

    def _get_user_vaccines_by_medical_record_id(
        self, id: int
    ) -> List[VacunasPorUsuario]:
        self._get_medical_record_by_id(id)
        return (
            self.__carelink_session.query(VacunasPorUsuario)
            .filter(VacunasPorUsuario.id_historiaClinica == id)
            .all()
        )
