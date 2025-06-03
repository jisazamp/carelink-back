from app.dto.v1.request.contracts import ContratoCreateDTO
from app.dto.v1.response.contracts import ContratoResponseDTO, ServicioContratoDTO
from app.exceptions.exceptions_classes import EntityNotFoundError
from app.models.activities import ActividadesGrupales, TipoActividad
from app.models.authorized_users import AuthorizedUsers
from app.models.cares_per_user import CuidadosEnfermeriaPorUsuario
from app.models.clinical_evolutions import EvolucionesClinicas
from app.models.contracts import (
    Contratos,
    Facturas,
    FechasServicio,
    MetodoPago,
    ServiciosPorContrato,
)
from app.models.family_member import FamilyMember
from app.models.family_members_by_user import FamiliaresYAcudientesPorUsuario
from app.models.interventions_per_user import IntervencionesPorUsuario
from app.models.medical_record import MedicalRecord
from app.models.medical_report import ReportesClinicos
from app.models.medicines_per_user import MedicamentosPorUsuario
from app.models.professional import Profesionales
from app.models.rates import TarifasServicioPorAnio
from app.models.user import User
from app.models.vaccines import VacunasPorUsuario
from boto3 import client
from botocore.exceptions import NoCredentialsError
from datetime import date, datetime
from fastapi import HTTPException, UploadFile
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
INVALID_CHARS = ["#", "@", "$", "%", " ", "&", "|", "(", ")", "-", "+"]


class CareLinkCrud:
    def __init__(self, carelink_db: Session) -> None:
        self.__carelink_session = carelink_db
        self.__s3_client = client("s3")

    def clean_string(self, string: str) -> str:
        cleaned_string = string
        for char in INVALID_CHARS:
            cleaned_string = cleaned_string.replace(char, "_")
        return cleaned_string

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

    def save_user(self, user: User, image: UploadFile | None) -> User:
        user.is_deleted = False
        self.__carelink_session.add(user)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(user)
        if image:
            image_url = self.upload_file_to_s3(
                image.file,
                "images-carelink",
                f"user_photos/{user.id_usuario}/{image.filename}",
            )
            user.url_imagen = image_url
        self.__carelink_session.commit()

        return user

    def save_family_member(self, id: int, kinship, family_member: FamilyMember):
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

    def save_user_medical_record(
        self,
        id: int,
        record: MedicalRecord,
        medicines: List[MedicamentosPorUsuario],
        cares: List[CuidadosEnfermeriaPorUsuario],
        interventions: List[IntervencionesPorUsuario],
        vaccines: List[VacunasPorUsuario],
        attachments: List[UploadFile],
    ):
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

        if attachments:
            for attachment in attachments:
                self.upload_file_to_s3(
                    attachment.file,
                    "images-carelink",
                    f"user_attachments/{id}/{attachment.filename}",
                )

        self.__carelink_session.commit()

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

    def save_activity(self, activity: ActividadesGrupales):
        self.__carelink_session.add(activity)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(activity)
        return activity

    def _update_user(self, user: User, db_user: User) -> User:
        for key, value in user.__dict__.items():
            if key != "_sa_instance_state":
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
        self,
        user_id: int,
        family_member: FamilyMember,
        kinship,
        db_family_member: FamilyMember,
    ) -> FamilyMember:
        kinship_string = kinship.dict()["parentezco"]

        for key, value in family_member.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_family_member, key):
                    setattr(db_family_member, key, value)

        association = (
            self.__carelink_session.query(FamiliaresYAcudientesPorUsuario)
            .filter_by(id_usuario=user_id, id_acudiente=db_family_member.id_acudiente)
            .first()
        )
        print(association)

        if association:
            association.parentesco = kinship_string

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

    def _update_activity(
        self, activity: ActividadesGrupales, db_activity: ActividadesGrupales
    ) -> ActividadesGrupales:
        for key, value in activity.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_activity, key):
                    setattr(db_activity, key, value)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_activity)
        return db_activity

    def update_user(
        self, user_id: int, user: User, photo: Optional[UploadFile] = None
    ) -> User:
        db_user = self._get_user_by_id(user_id)

        if db_user.url_imagen:
            old_photo_key = db_user.url_imagen.split("/")[-1]
            self.delete_s3_file(
                "images-carelink", f"user_photos/{user_id}/{old_photo_key}"
            )

        if photo:
            photo_url = self.upload_file_to_s3(
                photo.file,
                "images-carelink",
                f"user_photos/{user_id}/{photo.filename}",
            )
            user.url_imagen = photo_url
        elif user.url_imagen is None:
            self.delete_s3_folder("images-carelink", f"user_photos/{user_id}")
            user.url_imagen = None

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
        self.__carelink_session.commit()
        return record_to_update

    def update_medical_record(
        self, report_id: int, report: ReportesClinicos
    ) -> ReportesClinicos:
        db_report = self._get_medical_report_by_id(report_id)
        updated_report = self._update_record(report, db_report)
        return updated_report

    def update_activity(
        self, activity_id: int, activity: ActividadesGrupales
    ) -> ActividadesGrupales:
        db_activity = self._get_activity_by_id(activity_id)
        updated_activity = self._update_activity(activity, db_activity)
        return updated_activity

    def delete_user(self, user_id: int):
        db_user = self._get_user_by_id(user_id)
        db_user.is_deleted = True
        self.__carelink_session.commit()

    def delete_contract_by_id(self, contract_id: int):
        db_contract = self._get_contract_by_id(contract_id)
        self.__carelink_session.delete(db_contract)
        self.__carelink_session.commit()

    def delete_family_member(self, id: int):
        db_family_member, _ = self._get_family_member_by_id(id)
        db_family_member.is_deleted = True
        self.__carelink_session.commit()

    def delete_clinical_evolution(self, id: int):
        db_clinical_evolution = self._get_clinical_evolution_by_evolution_id(id)
        self.__carelink_session.delete(db_clinical_evolution)
        self.__carelink_session.commit()

    def delete_medical_report(self, id: int):
        db_clinical_evolution = self._get_medical_report_by_id(id)
        self.__carelink_session.delete(db_clinical_evolution)
        self.__carelink_session.commit()

    def delete_user_medical_record(self, record_id: int):
        db_record = self._get_medical_record_by_id(record_id)
        self.__carelink_session.delete(db_record)
        self.__carelink_session.commit()

    def delete_activity(self, activity_id: int):
        db_activity = self._get_activity_by_id(activity_id)
        self.__carelink_session.delete(db_activity)
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

    def _get_payment_methods(self) -> list[MetodoPago]:
        payment_methods = self.__carelink_session.query(MetodoPago).all()
        return payment_methods

    def _get_service_dates(self, service: ServiciosPorContrato) -> list[FechasServicio]:
        service_dates = (
            self.__carelink_session.query(FechasServicio)
            .filter(
                FechasServicio.id_servicio_contratado == service.id_servicio_contratado
            )
            .all()
        )
        return service_dates

    def _calculate_service_total(
        self, service: ServiciosPorContrato, contract_start_year: int
    ) -> float:
        rate = self._get_service_rate(service.id_servicio, contract_start_year)
        service_dates = self._get_service_dates(service)
        return rate.precio_por_dia * len(service_dates)

    def _calculate_contract_bill_total(self, contract_id: int) -> float:
        contract = self._get_contract_by_id(contract_id)
        contract_start_date = contract.fecha_inicio
        contract_start_year = contract_start_date.year
        contract_services = self._get_contract_services(contract_id)
        total = 0.0
        for contract_service in contract_services:
            result = self._calculate_service_total(
                contract_service, contract_start_year
            )
            total += result
        return total

    def calculate_partial_bill(
        self, service_ids: list[int], quantities: list[int], year: int
    ) -> float:
        total = 0.0
        for index, service_id in enumerate(service_ids):
            rate = self._get_service_rate(service_id, year)
            total += rate.precio_por_dia * quantities[index]
        return total

    def create_contract_bill(self, contract_id: int) -> Facturas:
        bill_total = self._calculate_contract_bill_total(contract_id)
        bill = Facturas(
            id_contrato=contract_id,
            fecha_emision=datetime.now(),
            total_factura=bill_total,
        )
        self.__carelink_session.add(bill)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(bill)
        return bill

    def _add_contract_services(
        self, contract_data: ContratoCreateDTO, contract: Contratos
    ) -> ServicioContratoDTO | None:
        servicio_dto = None

        for servicio in contract_data.servicios:
            servicio_contratado = ServiciosPorContrato(
                id_contrato=contract.id_contrato,
                id_servicio=servicio.id_servicio,
                fecha=servicio.fecha,
                descripcion=servicio.descripcion,
                precio_por_dia=servicio.precio_por_dia,
            )
            self.__carelink_session.add(servicio_contratado)
            self.__carelink_session.commit()
            self.__carelink_session.refresh(servicio_contratado)

            for f in servicio.fechas_servicio:
                fecha_servicio = FechasServicio(
                    id_servicio_contratado=servicio_contratado.id_servicio_contratado,
                    fecha=f.fecha,
                )
                self.__carelink_session.add(fecha_servicio)

            self.__carelink_session.commit()
            self.__carelink_session.refresh(servicio_contratado)

            if servicio_dto is None:
                servicio_dto = ServicioContratoDTO.from_orm(servicio_contratado)

        return servicio_dto

    def create_contract(self, contract_data: ContratoCreateDTO) -> Contratos:
        try:
            contrato = Contratos(
                id_usuario=contract_data.id_usuario,
                tipo_contrato=contract_data.tipo_contrato,
                fecha_inicio=contract_data.fecha_inicio,
                fecha_fin=contract_data.fecha_fin,
                facturar_contrato=contract_data.facturar_contrato,
            )
            self.__carelink_session.add(contrato)
            self.__carelink_session.commit()
            self.__carelink_session.refresh(contrato)
            self._add_contract_services(contract_data, contrato)
            return contrato
        except Exception as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error al crear contrato: {str(e)}"
            )

    def create_user_medical_record(
        self, user_id: int, record: MedicalRecord
    ) -> MedicalRecord:
        self._get_user_by_id(user_id)
        self.__carelink_session.add(record)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(record)
        return record

    def _get_service_rate(self, service_id: int, year: int) -> TarifasServicioPorAnio:
        rate = (
            self.__carelink_session.query(TarifasServicioPorAnio)
            .filter(
                TarifasServicioPorAnio.id_servicio == service_id,
                TarifasServicioPorAnio.anio == year,
            )
            .one()
        )
        if rate is None:
            raise EntityNotFoundError("Tarifa no encontrada")
        return rate

    def _get_contract_services(self, contract_id: int) -> list[ServiciosPorContrato]:
        services = (
            self.__carelink_session.query(ServiciosPorContrato)
            .filter(ServiciosPorContrato.id_contrato == contract_id)
            .all()
        )
        return services

    def _get_users(self) -> List[User]:
        users = (
            self.__carelink_session.query(User).filter(User.is_deleted == False).all()
        )
        return users

    def _get_contract_by_id(self, contract_id: int) -> Contratos:
        contract = (
            self.__carelink_session.query(Contratos)
            .filter(Contratos.id_contrato == contract_id)
            .first()
        )
        if contract is None:
            raise EntityNotFoundError(f"El contrato con id {contract_id} no existe")
        return contract

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

    def _get_professional_by_id(self, id: int) -> Profesionales:
        professional = (
            self.__carelink_session.query(Profesionales)
            .filter(Profesionales.id_profesional == id)
            .first()
        )
        if professional is None:
            raise EntityNotFoundError(f"Profesional con identificador #{id} no existe")
        return professional

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

    def _get_activities(self) -> List[ActividadesGrupales]:
        return self.__carelink_session.query(ActividadesGrupales).all()

    def _get_activity_by_id(self, id: int) -> ActividadesGrupales:
        activity = (
            self.__carelink_session.query(ActividadesGrupales)
            .filter(ActividadesGrupales.id == id)
            .first()
        )
        if activity is None:
            raise EntityNotFoundError(
                f"No se encuentra una actividad con el identificador #{id}"
            )
        return activity

    def _get_activity_types(self) -> List[TipoActividad]:
        return self.__carelink_session.query(TipoActividad).all()

    def _get_upcoming_activities(self) -> List[ActividadesGrupales]:
        today = date.today()
        upcoming_activities = (
            self.__carelink_session.query(ActividadesGrupales)
            .filter(ActividadesGrupales.fecha >= today)
            .order_by(ActividadesGrupales.fecha.asc())
            .all()
        )
        return upcoming_activities

    def upload_file_to_s3(self, file, bucket_name, object_name):
        try:
            self.__s3_client.upload_fileobj(file, bucket_name, object_name)
            return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        except NoCredentialsError:
            raise Exception("AWS credentials not available")

    def delete_s3_folder(self, bucket_name: str, folder_path: str):
        try:
            objects = self.__s3_client.list_objects_v2(
                Bucket=bucket_name, Prefix=folder_path
            )
            if "Contents" in objects:
                delete_keys = [{"Key": obj["Key"]} for obj in objects["Contents"]]
                self.__s3_client.delete_objects(
                    Bucket=bucket_name, Delete={"Objects": delete_keys}
                )
        except NoCredentialsError:
            raise Exception("AWS credentials not available")

    def delete_s3_file(self, bucket_name, object_name):
        try:
            self.__s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        except NoCredentialsError:
            raise Exception("AWS credentials not available")
