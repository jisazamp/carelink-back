from app.exceptions.exceptions_classes import BusinessLogicError, EntityNotFoundError
from app.models.authorized_users import AuthorizedUsers
from app.models.cares_per_user import CuidadosEnfermeriaPorUsuario
from app.models.clinical_evolutions import EvolucionesClinicas
from app.models.family_member import FamilyMember
from app.models.family_members_by_user import FamiliaresYAcudientesPorUsuario
from app.models.interventions_per_user import IntervencionesPorUsuario
from app.models.medical_record import MedicalRecord
from app.models.medical_report import ReportesClinicos
from app.models.medicines_per_user import MedicamentosPorUsuario
from app.models.professional import Profesionales
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

    def save_medical_report(self, report: ReportesClinicos):
        self.__carelink_session.add(report)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(report)
        return report

    def save_clinical_evolution(self, evolution: EvolucionesClinicas):
        self.__carelink_session.add(evolution)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(evolution)
        return evolution

    def _update_user(self, user: User, db_user: User) -> User:
        for key, value in user.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_user, key):
                    setattr(db_user, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_user)
        return db_user

    def _update_evolution(
        self, evolution: EvolucionesClinicas, db_evolution: EvolucionesClinicas
    ) -> EvolucionesClinicas:
        for key, value in evolution.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_evolution, key):
                    setattr(db_evolution, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_evolution)
        return db_evolution

    def _update_treatment(
        self, treatment: MedicamentosPorUsuario, db_treatment: MedicamentosPorUsuario
    ) -> MedicamentosPorUsuario:
        for key, value in treatment.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_treatment, key):
                    setattr(db_treatment, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_treatment)
        return db_treatment

    def _update_nursing(
        self,
        treatment: CuidadosEnfermeriaPorUsuario,
        db_treatment: CuidadosEnfermeriaPorUsuario,
    ) -> CuidadosEnfermeriaPorUsuario:
        for key, value in treatment.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_treatment, key):
                    setattr(db_treatment, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_treatment)
        return db_treatment

    def _update_intervention(
        self,
        treatment: IntervencionesPorUsuario,
        db_treatment: IntervencionesPorUsuario,
    ) -> IntervencionesPorUsuario:
        for key, value in treatment.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_treatment, key):
                    setattr(db_treatment, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_treatment)
        return db_treatment

    def _update_vaccine(
        self,
        treatment: VacunasPorUsuario,
        db_treatment: VacunasPorUsuario,
    ) -> VacunasPorUsuario:
        for key, value in treatment.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_treatment, key):
                    setattr(db_treatment, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_treatment)
        return db_treatment

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

    def _update_record(
        self, record: ReportesClinicos, db_record: ReportesClinicos
    ) -> ReportesClinicos:
        for key, value in record.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_record, key):
                    setattr(db_record, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_record)
        return db_record

    def update_user(self, user_id: int, user: User) -> User:
        db_user = self._get_user_by_id(user_id)
        updated_user = self._update_user(user, db_user)
        return updated_user

    def update_clinical_evolution(
        self, evolution_id: int, evolution: EvolucionesClinicas
    ) -> EvolucionesClinicas:
        db_evolution = self._get_clinical_evolution_by_evolution_id(evolution_id)
        updated_evolution = self._update_evolution(evolution, db_evolution)
        return updated_evolution

    def update_medical_treatment(
        self, treatment_id: int, treatment: MedicamentosPorUsuario
    ) -> MedicamentosPorUsuario:
        db_treatment = self._get_user_medical_treatment_by_id(treatment_id)
        updated_treatment = self._update_treatment(treatment, db_treatment)
        return updated_treatment

    def update_medical_nursing(
        self, treatment_id: int, treatment: CuidadosEnfermeriaPorUsuario
    ) -> CuidadosEnfermeriaPorUsuario:
        db_treatment = self._get_user_medical_nursing_by_id(treatment_id)
        updated_treatment = self._update_nursing(treatment, db_treatment)
        return updated_treatment

    def update_medical_intervention(
        self, treatment_id: int, treatment: IntervencionesPorUsuario
    ) -> IntervencionesPorUsuario:
        db_treatment = self._get_user_medical_intervention_by_id(treatment_id)
        updated_treatment = self._update_intervention(treatment, db_treatment)
        return updated_treatment

    def update_medical_vaccine(
        self, treatment_id: int, treatment: VacunasPorUsuario
    ) -> VacunasPorUsuario:
        db_treatment = self._get_user_medical_vaccine_by_id(treatment_id)
        updated_treatment = self._update_vaccine(treatment, db_treatment)
        return updated_treatment

    def update_family_member(
        self, family_member_id: int, family_member: FamilyMember
    ) -> FamilyMember:
        db_family_member, _ = self._get_family_member_by_id(family_member_id)
        updated_family_member = self._update_family_member(
            family_member, db_family_member
        )
        return updated_family_member

    def update_user_medical_record(
        self,
        user_id: int,
        record_id: int,
        update_data: dict,
        medicines: List[MedicamentosPorUsuario],
        cares: List[CuidadosEnfermeriaPorUsuario],
        interventions: List[IntervencionesPorUsuario],
        vaccines: List[VacunasPorUsuario],
    ) -> MedicalRecord:
        with self.__carelink_session.begin():
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

            for medicine in medicines:
                medicine.id_historiaClinica = record_to_update.id_historiaclinica
                self.__carelink_session.add(medicine)
            for care in cares:
                care.id_historiaClinica = record_to_update.id_historiaclinica
                self.__carelink_session.add(care)
            for intervention in interventions:
                intervention.id_historiaClinica = record_to_update.id_historiaclinica
                self.__carelink_session.add(intervention)
            for vaccine in vaccines:
                vaccine.id_historiaClinica = record_to_update.id_historiaclinica
                self.__carelink_session.add(vaccine)

            self.__carelink_session.flush()
            self.__carelink_session.refresh(record_to_update)
            return record_to_update

    def update_medical_record(
        self, report_id: int, report: ReportesClinicos
    ) -> ReportesClinicos:
        db_report = self._get_medical_record_by_id(report_id)
        updated_report = self._update_record(report, db_report)
        return updated_report

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

    def delete_user_vaccine_by_record_id(self, record_id: int, vaccine_id: int):
        db_vaccines = self._get_user_vaccines_by_medical_record_id(record_id)
        vaccines = []
        for vaccine in db_vaccines:
            vaccines.append(vaccine)
        db_vaccine = next((x for x in vaccines if x.id == vaccine_id), None)
        if not db_vaccine:
            raise EntityNotFoundError("No se encuentra la vacuna")
        self.__carelink_session.delete(db_vaccine)
        self.__carelink_session.commit()

    def delete_user_medicines_by_record_id(self, record_id: int, medicine_id: int):
        db_medicines = self._get_user_medicines_by_medical_record_id(record_id)
        medicines = []
        for medicine in db_medicines:
            medicines.append(medicine)
        db_medicine = next((x for x in medicines if x.id == medicine_id), None)
        if not db_medicine:
            raise EntityNotFoundError("No se encuentra el medicamento")
        self.__carelink_session.delete(db_medicine)
        self.__carelink_session.commit()

    def delete_user_care_by_record_id(self, record_id: int, care_id: int):
        db_cares = self._get_user_cares_by_medical_record_id(record_id)
        cares = []
        for care in db_cares:
            cares.append(care)
        db_care = next((x for x in cares if x.id == care_id), None)
        if not db_care:
            raise EntityNotFoundError("No se encuentra el cuidado")
        self.__carelink_session.delete(db_care)
        self.__carelink_session.commit()

    def delete_user_intervention_by_record_id(
        self, record_id: int, intervention_id: int
    ):
        db_interventions = self._get_user_interventions_by_medical_record_id(record_id)
        interventions = []
        for intervention in db_interventions:
            interventions.append(intervention)
        db_intervention = next(
            (x for x in interventions if x.id == intervention_id), None
        )
        if not db_intervention:
            raise EntityNotFoundError("No se encuentra la intervención")
        self.__carelink_session.delete(db_intervention)
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

    def _get_user_medical_treatment_by_id(self, id: int) -> MedicamentosPorUsuario:
        treatment = (
            self.__carelink_session.query(MedicamentosPorUsuario)
            .filter(MedicamentosPorUsuario.id == id)
            .first()
        )
        if treatment is None:
            raise EntityNotFoundError("Not found")
        return treatment

    def _get_user_medical_nursing_by_id(self, id: int) -> CuidadosEnfermeriaPorUsuario:
        treatment = (
            self.__carelink_session.query(CuidadosEnfermeriaPorUsuario)
            .filter(CuidadosEnfermeriaPorUsuario.id == id)
            .first()
        )
        if treatment is None:
            raise EntityNotFoundError("Not found")
        return treatment

    def _get_user_medical_intervention_by_id(self, id: int) -> IntervencionesPorUsuario:
        treatment = (
            self.__carelink_session.query(IntervencionesPorUsuario)
            .filter(IntervencionesPorUsuario.id == id)
            .first()
        )
        if treatment is None:
            raise EntityNotFoundError("Not found")
        return treatment

    def _get_user_medical_vaccine_by_id(self, id: int) -> VacunasPorUsuario:
        treatment = (
            self.__carelink_session.query(VacunasPorUsuario)
            .filter(VacunasPorUsuario.id == id)
            .first()
        )
        if treatment is None:
            raise EntityNotFoundError("Not found")
        return treatment

    def _get_medical_report_by_id(self, id: int) -> ReportesClinicos:
        db_reporte = (
            self.__carelink_session.query(ReportesClinicos)
            .filter(ReportesClinicos.id_reporteclinico == id)
            .first()
        )
        if db_reporte is None:
            raise EntityNotFoundError("Reporte Clinico not found")
        return db_reporte

    def _get_medical_reports_by_user_id(self, user_id: int) -> List[ReportesClinicos]:
        db_medical_record = self._get_user_medical_record_by_user_id(user_id)
        if db_medical_record is None:
            return []
        return (
            self.__carelink_session.query(ReportesClinicos)
            .filter(
                ReportesClinicos.id_historiaclinica
                == db_medical_record.id_historiaclinica
            )
            .all()
        )

    def _get_professionals(self) -> List[Profesionales]:
        return self.__carelink_session.query(Profesionales).all()

    def _get_clinical_evolutions_by_report_id(
        self, report_id: int
    ) -> List[EvolucionesClinicas]:
        return (
            self.__carelink_session.query(EvolucionesClinicas)
            .filter(EvolucionesClinicas.id_reporteclinico == report_id)
            .all()
        )

    def _get_clinical_evolution_by_evolution_id(
        self, evolution_id: int
    ) -> EvolucionesClinicas:
        evolucion = (
            self.__carelink_session.query(EvolucionesClinicas)
            .filter(EvolucionesClinicas.id_TipoReporte == evolution_id)
            .first()
        )
        if evolucion is None:
            raise EntityNotFoundError("No se encuentra el reporte clínico")
        return evolucion
