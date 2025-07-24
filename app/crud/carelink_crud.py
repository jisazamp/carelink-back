from app.dto.v1.request.contracts import ContratoCreateDTO
from app.dto.v1.request.payment_method import CreateUserPaymentRequestDTO
from app.dto.v1.response.contracts import ContratoResponseDTO, ServicioContratoDTO, FechaServicioDTO
from app.exceptions.exceptions_classes import EntityNotFoundError
from app.models.activities import ActividadesGrupales, TipoActividad
from app.models.authorized_users import AuthorizedUsers
from app.models.attendance_schedule import CronogramaAsistencia, CronogramaAsistenciaPacientes, EstadoAsistencia
from app.models.cares_per_user import CuidadosEnfermeriaPorUsuario
from app.models.clinical_evolutions import EvolucionesClinicas
from app.models.contracts import (
    Contratos,
    Facturas,
    DetalleFactura,
    FechasServicio,
    MetodoPago,
    Pagos,
    ServiciosPorContrato,
    TipoPago,
    Servicios,
    EstadoFactura,
)
from app.models.family_member import FamilyMember
from app.models.family_members_by_user import FamiliaresYAcudientesPorUsuario
from app.models.interventions_per_user import IntervencionesPorUsuario
from app.models.medical_record import MedicalRecord
from app.models.medical_report import ReportesClinicos
from app.models.medicines_per_user import MedicamentosPorUsuario
from app.models.professional import Profesionales
from app.models.rates import TarifasServicioPorAnio
from app.models.transporte import CronogramaTransporte, EstadoTransporte
from app.models.user import User
from app.models.vaccines import VacunasPorUsuario
from app.models.home_visit import VisitasDomiciliarias
from boto3 import client
from botocore.exceptions import NoCredentialsError
from datetime import date, datetime
from fastapi import HTTPException, UploadFile, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Tuple
from sqlalchemy.sql import func

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

    def list_users_with_home_visits(self) -> List[User]:
        return self._get_users_with_home_visits()

    def list_users_without_home_visits(self) -> List[User]:
        return self._get_users_without_home_visits()

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
        existing_user = self.__carelink_session.execute(
            select(User).where(
                User.email == user.email,
                User.is_deleted == False,
                User.id_usuario != user.id_usuario,
            )
        ).scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado para otro usuario.",
            )

        try:
            user.is_deleted = False
            self.__carelink_session.add(user)
            self.__carelink_session.commit()
            self.__carelink_session.refresh(user)

            if image:
                image_url = self.upload_file_to_s3(
                    image.file,
                    "images-care-link",
                    f"user_photos/{user.id_usuario}/{image.filename}",
                )
                user.url_imagen = image_url
                self.__carelink_session.commit()

            return user

        except SQLAlchemyError as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error al guardar el usuario.",
            )

    def create_home_visit(self, user_id: int, user_data: dict) -> VisitasDomiciliarias:
        """
        Crea una visita domiciliaria para un usuario cuando visitas_domiciliarias es True
        """
        from datetime import datetime, date, time

        # Crear visita domiciliaria con datos básicos
        visita_data = {
            "id_usuario": user_id,
            "id_contrato": None,  # Se asignará cuando se cree el contrato
            "fecha_visita": date.today(),
            "hora_visita": time(8, 0),  # Hora por defecto 8:00 AM
            "estado_visita": "PENDIENTE",
            "direccion_visita": user_data.get("direccion", ""),
            "telefono_visita": user_data.get("telefono", ""),
            "valor_dia": 0.00,
            "observaciones": f"Visita domiciliaria creada automáticamente para usuario {user_id}",
            "fecha_creacion": datetime.utcnow(),
            "fecha_actualizacion": datetime.utcnow()
        }

        visita = VisitasDomiciliarias(**visita_data)
        self.__carelink_session.add(visita)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(visita)

        return visita

    def save_family_member(self, id: int, kinship, family_member: FamilyMember):
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
                    "images-care-link",
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
        updated_user = self._update_user(user, db_user)

        if photo:
            image_url = self.upload_file_to_s3(
                photo.file,
                "images-care-link",
                f"user_photos/{user_id}/{photo.filename}",
            )
            updated_user.url_imagen = image_url
            self.__carelink_session.commit()

        return updated_user

    def update_clinical_evolution(
        self, evolution_id: int, evolution: EvolucionesClinicas
    ) -> EvolucionesClinicas:
        db_evolution = self._get_clinical_evolution_by_evolution_id(evolution_id)
        return self._update_evolution(evolution, db_evolution)

    def update_medical_treatment(
        self, treatment_id: int, treatment: MedicamentosPorUsuario
    ) -> MedicamentosPorUsuario:
        db_treatment = self._get_user_medical_treatment_by_id(treatment_id)
        return self._update_treatment(treatment, db_treatment)

    def update_medical_nursing(
        self, treatment_id: int, treatment: CuidadosEnfermeriaPorUsuario
    ) -> CuidadosEnfermeriaPorUsuario:
        db_treatment = self._get_user_medical_nursing_by_id(treatment_id)
        return self._update_nursing(treatment, db_treatment)

    def update_medical_intervention(
        self, treatment_id: int, treatment: IntervencionesPorUsuario
    ) -> IntervencionesPorUsuario:
        db_treatment = self._get_user_medical_intervention_by_id(treatment_id)
        return self._update_intervention(treatment, db_treatment)

    def update_medical_vaccine(
        self, treatment_id: int, treatment: VacunasPorUsuario
    ) -> VacunasPorUsuario:
        db_treatment = self._get_user_medical_vaccine_by_id(treatment_id)
        return self._update_vaccine(treatment, db_treatment)

    def update_family_member(
        self, family_member_id: int, family_member: FamilyMember
    ) -> FamilyMember:
        db_family_member = self._get_family_member_by_id(family_member_id)[0]
        return self._update_family_member(
            family_member_id, family_member, None, db_family_member
        )

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
        db_record = self._get_medical_record_by_id(record_id)

        for key, value in update_data.items():
            if hasattr(db_record, key):
                setattr(db_record, key, value)

        for medicine in medicines:
            medicine.id_historiaClinica = record_id
            self.__carelink_session.add(medicine)

        for care in cares:
            care.id_historiaClinica = record_id
            self.__carelink_session.add(care)

        for intervention in interventions:
            intervention.id_historiaClinica = record_id
            self.__carelink_session.add(intervention)

        for vaccine in vaccines:
            vaccine.id_historiaClinica = record_id
            self.__carelink_session.add(vaccine)

        self.__carelink_session.commit()
        self.__carelink_session.refresh(db_record)
        return db_record

    def update_medical_record(
        self, report_id: int, report: ReportesClinicos
    ) -> ReportesClinicos:
        db_report = self._get_medical_report_by_id(report_id)
        return self._update_record(report, db_report)

    def update_activity(
        self, activity_id: int, activity: ActividadesGrupales
    ) -> ActividadesGrupales:
        db_activity = self._get_activity_by_id(activity_id)
        return self._update_activity(activity, db_activity)

    def delete_user(self, user_id: int):
        user = self._get_user_by_id(user_id)
        user.is_deleted = True
        self.__carelink_session.commit()

    def delete_payment(self, payment_id: int):
        payment = self.get_payment_by_id(payment_id)
        self.__carelink_session.delete(payment)
        self.__carelink_session.commit()

    def delete_contract_by_id(self, contract_id: int):
        contract = self._get_contract_by_id(contract_id)
        self.__carelink_session.delete(contract)
        self.__carelink_session.commit()

    def delete_family_member(self, id: int):
        family_member = self._get_family_member_by_id(id)[0]
        self.__carelink_session.delete(family_member)
        self.__carelink_session.commit()

    def delete_clinical_evolution(self, id: int):
        evolution = self._get_clinical_evolution_by_evolution_id(id)
        self.__carelink_session.delete(evolution)
        self.__carelink_session.commit()

    def delete_medical_report(self, id: int):
        report = self._get_medical_report_by_id(id)
        self.__carelink_session.delete(report)
        self.__carelink_session.commit()

    def delete_user_medical_record(self, record_id: int):
        record = self._get_medical_record_by_id(record_id)
        self.__carelink_session.delete(record)
        self.__carelink_session.commit()

    def delete_activity(self, activity_id: int):
        activity = self._get_activity_by_id(activity_id)
        self.__carelink_session.delete(activity)
        self.__carelink_session.commit()

    def delete_user_vaccine_by_record_id(self, record_id: int, vaccine_id: int):
        vaccine = self.__carelink_session.execute(
            select(VacunasPorUsuario).where(
                VacunasPorUsuario.id_vacuna == vaccine_id,
                VacunasPorUsuario.id_historiaClinica == record_id,
            )
        ).scalar_one_or_none()
        if vaccine:
            self.__carelink_session.delete(vaccine)
            self.__carelink_session.commit()

    def delete_user_medicines_by_record_id(self, record_id: int, medicine_id: int):
        medicine = self.__carelink_session.execute(
            select(MedicamentosPorUsuario).where(
                MedicamentosPorUsuario.id_medicamento == medicine_id,
                MedicamentosPorUsuario.id_historiaClinica == record_id,
            )
        ).scalar_one_or_none()
        if medicine:
            self.__carelink_session.delete(medicine)
            self.__carelink_session.commit()

    def delete_user_care_by_record_id(self, record_id: int, care_id: int):
        care = self.__carelink_session.execute(
            select(CuidadosEnfermeriaPorUsuario).where(
                CuidadosEnfermeriaPorUsuario.id_cuidado == care_id,
                CuidadosEnfermeriaPorUsuario.id_historiaClinica == record_id,
            )
        ).scalar_one_or_none()
        if care:
            self.__carelink_session.delete(care)
            self.__carelink_session.commit()

    def delete_user_intervention_by_record_id(
        self, record_id: int, intervention_id: int
    ):
        intervention = self.__carelink_session.execute(
            select(IntervencionesPorUsuario).where(
                IntervencionesPorUsuario.id_intervencion == intervention_id,
                IntervencionesPorUsuario.id_historiaClinica == record_id,
            )
        ).scalar_one_or_none()
        if intervention:
            self.__carelink_session.delete(intervention)
            self.__carelink_session.commit()

    def authenticate_user(self, email: str, password: str) -> AuthorizedUsers | None:
        user = self.__carelink_session.execute(
            select(AuthorizedUsers).where(AuthorizedUsers.email == email)
        ).scalar_one_or_none()
        if user and pwd_context.verify(password, user.password):
            return user
        return None

    def update_factura_status(self, factura_id: int):
        factura = self.__carelink_session.execute(
            select(Facturas).where(Facturas.id_factura == factura_id)
        ).scalar_one_or_none()
        if factura:
            factura.estado = "PAGADA"
            self.__carelink_session.commit()

    def create_payment(self, payment_data: Pagos) -> Pagos:
        self.__carelink_session.add(payment_data)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(payment_data)
        return payment_data

    def create_user(self, user_data: AuthorizedUsers) -> AuthorizedUsers:
        self.__carelink_session.add(user_data)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(user_data)
        return user_data

    def get_contract_bill(self, contract_id: int) -> Facturas:
        return self.__carelink_session.execute(
            select(Facturas).where(Facturas.id_contrato == contract_id)
        ).scalar_one_or_none()

    def get_payment_by_id(self, payment_id: int) -> Pagos:
        return self.__carelink_session.execute(
            select(Pagos).where(Pagos.id_pago == payment_id)
        ).scalar_one_or_none()

    def _get_payment_methods(self) -> list[MetodoPago]:
        return self.__carelink_session.execute(select(MetodoPago)).scalars().all()

    def _get_payment_types(self) -> list[TipoPago]:
        return self.__carelink_session.execute(select(TipoPago)).scalars().all()

    def get_bill_by_id(self, bill_id: int) -> Facturas:
        return self.__carelink_session.execute(
            select(Facturas).where(Facturas.id_factura == bill_id)
        ).scalar_one_or_none()

    def _get_service_dates(self, service: ServiciosPorContrato) -> list[FechasServicio]:
        return self.__carelink_session.execute(
            select(FechasServicio).where(
                FechasServicio.id_servicio_contratado == service.id_servicio_contratado
            )
        ).scalars().all()

    def _calculate_service_total(
        self, service: ServiciosPorContrato, contract_start_year: int
    ) -> float:
        service_rate = self._get_service_rate(service.id_servicio, contract_start_year)
        return service_rate.tarifa * service.cantidad

    def _calculate_contract_bill_total(self, contract_id: int) -> float:
        services = self._get_contract_services(contract_id)
        return sum(
            self._calculate_service_total(service, contract_start_year=2024)
            for service in services
        )

    def calculate_partial_bill(
        self, service_ids: list[int], quantities: list[int], year: int
    ) -> float:
        total = 0
        for service_id, quantity in zip(service_ids, quantities):
            rate = self._get_service_rate(service_id, year)
            total += rate.tarifa * quantity
        return total

    def create_contract_bill(self, contract_id: int) -> Facturas:
        total = self._calculate_contract_bill_total(contract_id)
        bill = Facturas(
            id_contrato=contract_id,
            total_factura=total,
            estado="PENDIENTE",
            fecha_creacion=datetime.utcnow(),
        )
        self.__carelink_session.add(bill)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(bill)
        return bill

    def create_contract(self, contract_data: ContratoCreateDTO) -> dict:
        contract = Contratos(
            id_usuario=contract_data.id_usuario,
            tipo_contrato=contract_data.tipo_contrato,
            fecha_inicio=contract_data.fecha_inicio,
            fecha_fin=contract_data.fecha_fin,
            facturar_contrato=contract_data.facturar_contrato,
            estado=contract_data.estado,
        )
        self.__carelink_session.add(contract)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(contract)
        return {"id_contrato": contract.id_contrato}

    def create_user_medical_record(
        self, user_id: int, record: MedicalRecord
    ) -> MedicalRecord:
        self._get_user_by_id(user_id)
        self.__carelink_session.add(record)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(record)
        return record

    def _get_service_rate(self, service_id: int, year: int) -> TarifasServicioPorAnio:
        return self.__carelink_session.execute(
            select(TarifasServicioPorAnio).where(
                TarifasServicioPorAnio.id_servicio == service_id,
                TarifasServicioPorAnio.anio == year,
            )
        ).scalar_one_or_none()

    def _get_contract_services(self, contract_id: int) -> list[ServiciosPorContrato]:
        return self.__carelink_session.execute(
            select(ServiciosPorContrato).where(
                ServiciosPorContrato.id_contrato == contract_id
            )
        ).scalars().all()

    def _get_users(self) -> List[User]:
        return self.__carelink_session.execute(
            select(User).where(User.is_deleted == False)
        ).scalars().all()

    def _get_users_with_home_visits(self) -> List[User]:
        return self.__carelink_session.execute(
            select(User).where(
                User.is_deleted == False,
                User.visitas_domiciliarias == True
            )
        ).scalars().all()

    def _get_users_without_home_visits(self) -> List[User]:
        return self.__carelink_session.execute(
            select(User).where(
                User.is_deleted == False,
                User.visitas_domiciliarias == False
            )
        ).scalars().all()

    def get_all_contracts(self) -> List[ContratoResponseDTO]:
        contracts = self.__carelink_session.execute(select(Contratos)).scalars().all()
        return [
            ContratoResponseDTO(
                id_contrato=contract.id_contrato,
                id_usuario=contract.id_usuario,
                tipo_contrato=contract.tipo_contrato,
                fecha_inicio=contract.fecha_inicio,
                fecha_fin=contract.fecha_fin,
                facturar_contrato=contract.facturar_contrato,
                estado=contract.estado,
                servicios=[],
                fechas_servicio=[],
            )
            for contract in contracts
        ]

    def _get_contract_by_id(self, contract_id: int) -> Contratos:
        contract = self.__carelink_session.execute(
            select(Contratos).where(Contratos.id_contrato == contract_id)
        ).scalar_one_or_none()
        if not contract:
            raise EntityNotFoundError(f"Contrato con ID {contract_id} no encontrado")
        return contract

    def _get_user_by_id(self, user_id: int) -> User:
        user = self.__carelink_session.execute(
            select(User).where(
                User.id_usuario == user_id, User.is_deleted == False
            )
        ).scalar_one_or_none()
        if not user:
            raise EntityNotFoundError(f"Usuario con ID {user_id} no encontrado")
        return user

    def _get_authorized_user_info(self, user_id) -> AuthorizedUsers:
        return self.__carelink_session.execute(
            select(AuthorizedUsers).where(AuthorizedUsers.id == user_id)
        ).scalar_one_or_none()

    def _get_family_members_by_user_id(
        self, user_id: int
    ) -> List[FamiliaresYAcudientesPorUsuario]:
        return self.__carelink_session.execute(
            select(FamiliaresYAcudientesPorUsuario).where(
                FamiliaresYAcudientesPorUsuario.id_usuario == user_id
            )
        ).scalars().all()

    def _get_family_members(self) -> List[FamilyMember]:
        return self.__carelink_session.execute(select(FamilyMember)).scalars().all()

    def _get_family_member_by_id(self, id: int) -> Tuple[FamilyMember, str]:
        family_member = self.__carelink_session.execute(
            select(FamilyMember).where(FamilyMember.id_acudiente == id)
        ).scalar_one_or_none()
        if not family_member:
            raise EntityNotFoundError(f"Acudiente con ID {id} no encontrado")
        return family_member, ""

    def _get_user_medical_record_by_user_id(self, id: int) -> MedicalRecord | None:
        return self.__carelink_session.execute(
            select(MedicalRecord).where(MedicalRecord.id_usuario == id)
        ).scalar_one_or_none()

    def _get_medical_record_by_id(self, id: int) -> MedicalRecord:
        record = self.__carelink_session.execute(
            select(MedicalRecord).where(MedicalRecord.id_historiaclinica == id)
        ).scalar_one_or_none()
        if not record:
            raise EntityNotFoundError(f"Historia clínica con ID {id} no encontrada")
        return record

    def _get_user_medicines_by_medical_record_id(
        self, id: int
    ) -> List[MedicamentosPorUsuario]:
        return self.__carelink_session.execute(
            select(MedicamentosPorUsuario).where(
                MedicamentosPorUsuario.id_historiaClinica == id
            )
        ).scalars().all()

    def _get_user_cares_by_medical_record_id(
        self, id: int
    ) -> List[CuidadosEnfermeriaPorUsuario]:
        return self.__carelink_session.execute(
            select(CuidadosEnfermeriaPorUsuario).where(
                CuidadosEnfermeriaPorUsuario.id_historiaClinica == id
            )
        ).scalars().all()

    def _get_user_interventions_by_medical_record_id(
        self, id: int
    ) -> List[IntervencionesPorUsuario]:
        return self.__carelink_session.execute(
            select(IntervencionesPorUsuario).where(
                IntervencionesPorUsuario.id_historiaClinica == id
            )
        ).scalars().all()

    def _get_user_vaccines_by_medical_record_id(
        self, id: int
    ) -> List[VacunasPorUsuario]:
        return self.__carelink_session.execute(
            select(VacunasPorUsuario).where(
                VacunasPorUsuario.id_historiaClinica == id
            )
        ).scalars().all()

    def _get_user_medical_treatment_by_id(self, id: int) -> MedicamentosPorUsuario:
        treatment = self.__carelink_session.execute(
            select(MedicamentosPorUsuario).where(
                MedicamentosPorUsuario.id_medicamento == id
            )
        ).scalar_one_or_none()
        if not treatment:
            raise EntityNotFoundError(f"Tratamiento con ID {id} no encontrado")
        return treatment

    def _get_user_medical_nursing_by_id(self, id: int) -> CuidadosEnfermeriaPorUsuario:
        nursing = self.__carelink_session.execute(
            select(CuidadosEnfermeriaPorUsuario).where(
                CuidadosEnfermeriaPorUsuario.id_cuidado == id
            )
        ).scalar_one_or_none()
        if not nursing:
            raise EntityNotFoundError(f"Cuidado de enfermería con ID {id} no encontrado")
        return nursing

    def _get_user_medical_intervention_by_id(self, id: int) -> IntervencionesPorUsuario:
        intervention = self.__carelink_session.execute(
            select(IntervencionesPorUsuario).where(
                IntervencionesPorUsuario.id_intervencion == id
            )
        ).scalar_one_or_none()
        if not intervention:
            raise EntityNotFoundError(f"Intervención con ID {id} no encontrada")
        return intervention

    def _get_user_medical_vaccine_by_id(self, id: int) -> VacunasPorUsuario:
        vaccine = self.__carelink_session.execute(
            select(VacunasPorUsuario).where(VacunasPorUsuario.id_vacuna == id)
        ).scalar_one_or_none()
        if not vaccine:
            raise EntityNotFoundError(f"Vacuna con ID {id} no encontrada")
        return vaccine

    def _get_medical_report_by_id(self, id: int) -> ReportesClinicos:
        report = self.__carelink_session.execute(
            select(ReportesClinicos).where(ReportesClinicos.id_reporteclinico == id)
        ).scalar_one_or_none()
        if not report:
            raise EntityNotFoundError(f"Reporte clínico con ID {id} no encontrado")
        return report

    def _get_medical_reports_by_user_id(self, user_id: int) -> List[ReportesClinicos]:
        return self.__carelink_session.execute(
            select(ReportesClinicos).where(ReportesClinicos.id_historiaclinica == user_id)
        ).scalars().all()

    def _get_professionals(self) -> List[Profesionales]:
        return self.__carelink_session.execute(select(Profesionales)).scalars().all()

    def _get_professional_by_id(self, id: int) -> Profesionales:
        professional = self.__carelink_session.execute(
            select(Profesionales).where(Profesionales.id_profesional == id)
        ).scalar_one_or_none()
        if not professional:
            raise EntityNotFoundError(f"Profesional con ID {id} no encontrado")
        return professional

    def _get_clinical_evolutions_by_report_id(
        self, report_id: int
    ) -> List[EvolucionesClinicas]:
        return self.__carelink_session.execute(
            select(EvolucionesClinicas).where(
                EvolucionesClinicas.id_reporteclinico == report_id
            )
        ).scalars().all()

    def _get_clinical_evolution_by_evolution_id(
        self, evolution_id: int
    ) -> EvolucionesClinicas:
        evolution = self.__carelink_session.execute(
            select(EvolucionesClinicas).where(
                EvolucionesClinicas.id_evolucionclinica == evolution_id
            )
        ).scalar_one_or_none()
        if not evolution:
            raise EntityNotFoundError(f"Evolución clínica con ID {evolution_id} no encontrada")
        return evolution

    def _get_activities(self) -> List[ActividadesGrupales]:
        return self.__carelink_session.execute(select(ActividadesGrupales)).scalars().all()

    def _get_activity_by_id(self, id: int) -> ActividadesGrupales:
        activity = self.__carelink_session.execute(
            select(ActividadesGrupales).where(ActividadesGrupales.id_actividad == id)
        ).scalar_one_or_none()
        if not activity:
            raise EntityNotFoundError(f"Actividad con ID {id} no encontrada")
        return activity

    def _get_activity_types(self) -> List[TipoActividad]:
        return self.__carelink_session.execute(select(TipoActividad)).scalars().all()

    def _get_upcoming_activities(self) -> List[ActividadesGrupales]:
        return self.__carelink_session.execute(
            select(ActividadesGrupales).where(
                ActividadesGrupales.fecha_actividad >= date.today()
            )
        ).scalars().all()

    def upload_file_to_s3(self, file, bucket_name, object_name):
        try:
            self.__s3_client.upload_fileobj(file, bucket_name, object_name)
            return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        except NoCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Credenciales de AWS no configuradas",
            )

    def delete_s3_folder(self, bucket_name: str, folder_path: str):
        try:
            objects = self.__s3_client.list_objects_v2(
                Bucket=bucket_name, Prefix=folder_path
            )
            if "Contents" in objects:
                for obj in objects["Contents"]:
                    self.__s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
        except NoCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Credenciales de AWS no configuradas",
            )

    def delete_s3_file(self, bucket_name, object_name):
        try:
            self.__s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        except NoCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Credenciales de AWS no configuradas",
            )

def get_bill_payments_total(db, id_factura: int) -> float:
    """
    Retorna el total de pagos asociados a una factura
    """
    from app.models.contracts import Pagos
    pagos = db.query(Pagos).filter(Pagos.id_factura == id_factura).all()
    total = sum(float(pago.valor) for pago in pagos)
    return total
