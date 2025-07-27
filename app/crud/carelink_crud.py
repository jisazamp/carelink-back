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

        if photo:
            self.delete_s3_folder("images-care-link", f"user_photos/{user_id}")
            photo_url = self.upload_file_to_s3(
                photo.file,
                "images-care-link",
                f"user_photos/{user_id}/{photo.filename}",
            )
            user.url_imagen = photo_url
        
        updated_user = self._update_user(user, db_user)
        return updated_user

    def delete_user_photo(self, user_id: int):
        self.delete_s3_folder("images-care-link", f"user_photo/{user_id}")
        user = self._get_user_by_id(user_id)
        user.url_imagen = None
        self.__carelink_session.commit() 

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

    def delete_payment(self, payment_id: int):
        db_payment = self.get_payment_by_id(payment_id)
        self.__carelink_session.delete(db_payment)
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

    def update_factura_status(self, factura_id: int):
        """
        Actualiza el estado de la factura según los pagos realizados
        Si los pagos cubren el total, estado = "PAGADA"
        Si no, estado = "PENDIENTE"
        """
        try:
            # Obtener la factura
            factura = self.__carelink_session.query(Facturas).filter(
                Facturas.id_factura == factura_id
            ).first()
            
            if not factura:
                raise HTTPException(
                    status_code=404,
                    detail=f"Factura con ID {factura_id} no encontrada"
                )
            
            # Calcular total de pagos
            total_pagado = self.__carelink_session.query(func.sum(Pagos.valor)).filter(
                Pagos.id_factura == factura_id
            ).scalar() or 0
            
            # Determinar estado según pagos
            if total_pagado >= float(factura.total_factura):
                factura.estado_factura = EstadoFactura.PAGADA
            else:
                factura.estado_factura = EstadoFactura.PENDIENTE
            
            self.__carelink_session.commit()
            self.__carelink_session.refresh(factura)
            
            return factura
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al actualizar estado de factura: {str(e)}"
            )

    def create_payment(self, payment_data: Pagos) -> Pagos:
        try:
            # Validar que la factura existe
            bill = self.get_bill_by_id(payment_data.id_factura)
            if not bill:
                raise EntityNotFoundError("Factura no encontrada")

            # Validar que el método de pago existe
            payment_method = self.__carelink_session.query(MetodoPago).filter(
                MetodoPago.id_metodo_pago == payment_data.id_metodo_pago
            ).first()
            if not payment_method:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Método de pago con ID {payment_data.id_metodo_pago} no existe"
                )

            # Validar que el tipo de pago existe
            payment_type = self.__carelink_session.query(TipoPago).filter(
                TipoPago.id_tipo_pago == payment_data.id_tipo_pago
            ).first()
            if not payment_type:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Tipo de pago con ID {payment_data.id_tipo_pago} no existe"
                )

            # Validar tipo de pago total: solo un pago permitido
            tipo_pago = payment_data.id_tipo_pago
            if tipo_pago == 1:  # 1 = Total
                pagos_existentes = self.__carelink_session.query(Pagos).filter(
                    Pagos.id_factura == payment_data.id_factura
                ).count()
                if pagos_existentes > 0:
                    raise HTTPException(
                        status_code=400, 
                        detail="Solo se permite un pago total por factura"
                    )
                # Permitir pagos parciales - no validar que sea igual al total
                # El pago total puede ser menor al total de la factura

            # Validar que el valor del pago no exceda el total de la factura
            total_pagado = self.__carelink_session.query(Pagos).filter(
                Pagos.id_factura == payment_data.id_factura
            ).with_entities(func.sum(Pagos.valor)).scalar() or 0
            
            if float(total_pagado) + float(payment_data.valor) > float(bill.total_factura):
                raise HTTPException(
                    status_code=400,
                    detail="El valor del pago excede el total pendiente de la factura"
                )

            # Crear el pago
            payment = Pagos(
                id_factura=payment_data.id_factura,
                id_metodo_pago=payment_data.id_metodo_pago,
                id_tipo_pago=payment_data.id_tipo_pago,
                fecha_pago=payment_data.fecha_pago,
                valor=payment_data.valor,
            )

            self.__carelink_session.add(payment)
            self.__carelink_session.commit()
            self.__carelink_session.refresh(payment)

            # Actualizar estado de la factura
            self.update_factura_status(payment.id_factura)

            return payment

        except HTTPException:
            # Re-lanzar HTTPExceptions para mantener el status code
            self.__carelink_session.rollback()
            raise
        except Exception as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Error al crear el pago: {str(e)}"
            )

    def create_user(self, user_data: AuthorizedUsers) -> AuthorizedUsers:
        self.__carelink_session.add(user_data)
        self.__carelink_session.commit()
        return user_data

    def get_contract_bill(self, contract_id: int) -> Facturas:
        bill = (
            self.__carelink_session.query(Facturas)
            .filter(Facturas.id_contrato == contract_id)
            .first()
        )

        if bill is None:
            raise EntityNotFoundError(
                "No se encuentran facturas registradas para este contrato"
            )

        return bill

    def get_payment_by_id(self, payment_id: int) -> Pagos:
        payment = (
            self.__carelink_session.query(Pagos)
            .filter(Pagos.id_pago == payment_id)
            .first()
        )
        if payment is None:
            raise EntityNotFoundError(
                f"No existe un pago con identificador {payment_id}"
            )
        return payment

    def _get_payment_methods(self) -> list[MetodoPago]:
        payment_methods = self.__carelink_session.query(MetodoPago).all()
        return payment_methods

    def _get_payment_types(self) -> list[TipoPago]:
        payment_types = self.__carelink_session.query(TipoPago).all()
        return payment_types

    def get_bill_by_id(self, bill_id: int) -> Facturas:
        bill = (
            self.__carelink_session.query(Facturas)
            .filter(Facturas.id_factura == bill_id)
            .first()
        )
        if bill is None:
            raise EntityNotFoundError(
                f"No hay factura registrada con el identificador {bill_id}"
            )
        return bill

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
        
        # Generar numero_factura basado en id_factura (relleno de ceros a la izquierda)
        numero_factura = str(bill.id_factura).zfill(4)
        bill.numero_factura = numero_factura
        self.__carelink_session.commit()
        self.__carelink_session.refresh(bill)
        
        return bill

    def create_contract(self, contract_data: ContratoCreateDTO) -> dict:
        """
        Crea un contrato y los servicios asociados, retornando el contrato y los IDs de ServiciosPorContrato generados.
        """
        self.actualizar_estados_contratos_finalizados()
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
            # Insertar servicios y recolectar IDs
            servicios_ids = []
            for servicio in contract_data.servicios:
                servicio_contratado = ServiciosPorContrato(
                    id_contrato=contrato.id_contrato,
                    id_servicio=servicio.id_servicio,
                    fecha=servicio.fecha,
                    descripcion=servicio.descripcion,
                    precio_por_dia=servicio.precio_por_dia,
                )
                self.__carelink_session.add(servicio_contratado)
                self.__carelink_session.commit()
                self.__carelink_session.refresh(servicio_contratado)
                servicios_ids.append({
                    'id_servicio_contratado': servicio_contratado.id_servicio_contratado,
                    'id_servicio': servicio_contratado.id_servicio
                })
                for f in servicio.fechas_servicio:
                    fecha_servicio = FechasServicio(
                        id_servicio_contratado=servicio_contratado.id_servicio_contratado,
                        fecha=f.fecha,
                    )
                    self.__carelink_session.add(fecha_servicio)
                self.__carelink_session.commit()
            return {
                'contrato': contrato,
                'servicios_por_contrato': servicios_ids
            }
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

    def get_all_contracts(self) -> List[ContratoResponseDTO]:
        """Obtener todos los contratos del sistema"""
        self.actualizar_estados_contratos_finalizados()
        try:
            contratos = self.__carelink_session.query(Contratos).all()
            contratos_response = []
            
            for contrato in contratos:
                # Obtener servicios del contrato
                servicios = self.__carelink_session.query(ServiciosPorContrato).filter(
                    ServiciosPorContrato.id_contrato == contrato.id_contrato
                ).all()
                
                servicios_dto = []
                for servicio in servicios:
                    # Obtener fechas de servicio
                    fechas = self.__carelink_session.query(FechasServicio).filter(
                        FechasServicio.id_servicio_contratado == servicio.id_servicio_contratado
                    ).all()
                    
                    fechas_dto = [FechaServicioDTO(fecha=fecha.fecha) for fecha in fechas]
                    
                    servicio_dto = ServicioContratoDTO(
                        id_servicio_contratado=servicio.id_servicio_contratado,
                        id_servicio=servicio.id_servicio,
                        fecha=servicio.fecha,
                        descripcion=servicio.descripcion,
                        precio_por_dia=float(servicio.precio_por_dia),
                        fechas_servicio=fechas_dto
                    )
                    servicios_dto.append(servicio_dto)
                
                contrato_dto = ContratoResponseDTO(
                    id_contrato=contrato.id_contrato,
                    id_usuario=contrato.id_usuario,
                    tipo_contrato=contrato.tipo_contrato,
                    fecha_inicio=contrato.fecha_inicio,
                    fecha_fin=contrato.fecha_fin,
                    facturar_contrato=contrato.facturar_contrato,
                    estado=contrato.estado,
                    servicios=servicios_dto
                )
                contratos_response.append(contrato_dto)
            
            return contratos_response
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener contratos: {str(e)}"
            )

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

    # ==================== MÉTODOS DE CRONOGRAMA DE ASISTENCIA ====================
    
    def create_cronograma_asistencia(self, cronograma_data) -> CronogramaAsistencia:
        """Crear un nuevo cronograma de asistencia"""
        try:
            cronograma = CronogramaAsistencia(**cronograma_data.dict())
            self.__carelink_session.add(cronograma)
            self.__carelink_session.commit()
            self.__carelink_session.refresh(cronograma)
            return cronograma
        except SQLAlchemyError as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear cronograma de asistencia: {str(e)}"
            )

    def add_paciente_to_cronograma(self, paciente_data) -> CronogramaAsistenciaPacientes:
        """Agregar un paciente a un cronograma de asistencia"""
        try:
            # Verificar que el cronograma existe
            cronograma = self._get_cronograma_by_id(paciente_data.id_cronograma)
            
            # Verificar que el usuario existe
            usuario = self._get_user_by_id(paciente_data.id_usuario)
            
            # Verificar que no haya doble reserva para el mismo paciente en la misma fecha
            existing_booking = self.__carelink_session.query(CronogramaAsistenciaPacientes).join(
                CronogramaAsistencia
            ).filter(
                CronogramaAsistenciaPacientes.id_usuario == paciente_data.id_usuario,
                CronogramaAsistencia.fecha == cronograma.fecha
            ).first()
            
            if existing_booking:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El paciente ya tiene una cita agendada para la fecha {cronograma.fecha}"
                )
            
            paciente = CronogramaAsistenciaPacientes(**paciente_data.dict())
            self.__carelink_session.add(paciente)
            self.__carelink_session.commit()
            self.__carelink_session.refresh(paciente)
            return paciente
        except SQLAlchemyError as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al agregar paciente al cronograma: {str(e)}"
            )

    def update_estado_asistencia(self, id_cronograma_paciente: int, estado_data) -> CronogramaAsistenciaPacientes:
        """Actualizar el estado de asistencia de un paciente"""
        try:
            paciente = self._get_cronograma_paciente_by_id(id_cronograma_paciente)
            
            # Actualizar estado
            paciente.estado_asistencia = estado_data.estado_asistencia
            if estado_data.observaciones:
                paciente.observaciones = estado_data.observaciones
            
            self.__carelink_session.commit()
            self.__carelink_session.refresh(paciente)
            return paciente
        except SQLAlchemyError as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar estado de asistencia: {str(e)}"
            )

    def reagendar_paciente(self, id_cronograma_paciente: int, estado_data) -> CronogramaAsistenciaPacientes:
        """Reagendar un paciente a una nueva fecha"""
        try:
            paciente = self._get_cronograma_paciente_by_id(id_cronograma_paciente)
            
            # Verificar que el paciente esté en estado PENDIENTE
            if paciente.estado_asistencia != EstadoAsistencia.PENDIENTE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo se pueden reagendar pacientes con estado PENDIENTE"
                )
            
            # Buscar o crear un cronograma para la nueva fecha
            nuevo_cronograma = self.__carelink_session.query(CronogramaAsistencia).filter(
                CronogramaAsistencia.fecha == estado_data.nueva_fecha,
                CronogramaAsistencia.id_profesional == paciente.cronograma.id_profesional
            ).first()
            
            if not nuevo_cronograma:
                # Crear nuevo cronograma para la fecha
                nuevo_cronograma = CronogramaAsistencia(
                    id_profesional=paciente.cronograma.id_profesional,
                    fecha=estado_data.nueva_fecha,
                    comentario=f"Reagendamiento desde {paciente.cronograma.fecha}"
                )
                self.__carelink_session.add(nuevo_cronograma)
                self.__carelink_session.flush()
            
            # Crear nuevo registro de paciente en el nuevo cronograma
            nuevo_paciente = CronogramaAsistenciaPacientes(
                id_cronograma=nuevo_cronograma.id_cronograma,
                id_usuario=paciente.id_usuario,
                id_contrato=paciente.id_contrato,
                estado_asistencia=EstadoAsistencia.PENDIENTE,
                requiere_transporte=paciente.requiere_transporte,
                observaciones=f"Reagendado desde {paciente.cronograma.fecha}. {estado_data.observaciones or ''}"
            )
            
            # Marcar el paciente original como reagendado
            paciente.estado_asistencia = EstadoAsistencia.REAGENDADO
            paciente.observaciones = f"Reagendado a {estado_data.nueva_fecha}. {estado_data.observaciones or ''}"
            
            self.__carelink_session.add(nuevo_paciente)
            self.__carelink_session.commit()
            self.__carelink_session.refresh(nuevo_paciente)
            return nuevo_paciente
        except SQLAlchemyError as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al reagendar paciente: {str(e)}"
            )

    def get_cronogramas_por_rango(self, fecha_inicio: str, fecha_fin: str) -> List[CronogramaAsistencia]:
        """Obtener cronogramas por rango de fechas"""
        try:
            cronogramas = self.__carelink_session.query(CronogramaAsistencia).filter(
                CronogramaAsistencia.fecha >= fecha_inicio,
                CronogramaAsistencia.fecha <= fecha_fin
            ).order_by(CronogramaAsistencia.fecha.asc()).all()
            
            return cronogramas
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener cronogramas: {str(e)}"
            )

    def get_cronogramas_por_profesional(self, id_profesional: int) -> List[CronogramaAsistencia]:
        """Obtener cronogramas por profesional"""
        try:
            # Verificar que el profesional existe
            self._get_professional_by_id(id_profesional)
            
            cronogramas = self.__carelink_session.query(CronogramaAsistencia).filter(
                CronogramaAsistencia.id_profesional == id_profesional
            ).order_by(CronogramaAsistencia.fecha.asc()).all()
            
            return cronogramas
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener cronogramas del profesional: {str(e)}"
            )

    def _get_cronograma_by_id(self, id_cronograma: int) -> CronogramaAsistencia:
        """Obtener cronograma por ID"""
        cronograma = self.__carelink_session.query(CronogramaAsistencia).filter(
            CronogramaAsistencia.id_cronograma == id_cronograma
        ).first()
        
        if not cronograma:
            raise EntityNotFoundError(f"Cronograma con ID {id_cronograma} no encontrado")
        
        return cronograma

    def _get_cronograma_paciente_by_id(self, id_cronograma_paciente: int) -> CronogramaAsistenciaPacientes:
        """Obtener paciente de cronograma por ID"""
        paciente = self.__carelink_session.query(CronogramaAsistenciaPacientes).filter(
            CronogramaAsistenciaPacientes.id_cronograma_paciente == id_cronograma_paciente
        ).first()
        
        if not paciente:
            raise EntityNotFoundError(f"Paciente de cronograma con ID {id_cronograma_paciente} no encontrado")
        
        return paciente

    # ==================== MÉTODOS DE TRANSPORTE ====================
    
    def create_transporte(self, transporte_data) -> CronogramaTransporte:
        """Crear un nuevo registro de transporte"""
        try:
            # Verificar que el paciente del cronograma existe
            self._get_cronograma_paciente_by_id(transporte_data.id_cronograma_paciente)
            
            transporte = CronogramaTransporte(**transporte_data.dict())
            self.__carelink_session.add(transporte)
            self.__carelink_session.commit()
            self.__carelink_session.refresh(transporte)
            return transporte
        except SQLAlchemyError as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear transporte: {str(e)}"
            )

    def update_transporte(self, id_transporte: int, transporte_data) -> CronogramaTransporte:
        """Actualizar un registro de transporte"""
        try:
            transporte = self._get_transporte_by_id(id_transporte)
            
            for key, value in transporte_data.dict(exclude_unset=True).items():
                if hasattr(transporte, key):
                    setattr(transporte, key, value)
            
            self.__carelink_session.commit()
            self.__carelink_session.refresh(transporte)
            return transporte
        except SQLAlchemyError as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar transporte: {str(e)}"
            )

    def delete_transporte(self, id_transporte: int):
        """Eliminar un registro de transporte"""
        try:
            transporte = self._get_transporte_by_id(id_transporte)
            self.__carelink_session.delete(transporte)
            self.__carelink_session.commit()
        except SQLAlchemyError as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar transporte: {str(e)}"
            )

    def get_ruta_diaria(self, fecha: str) -> List[dict]:
        """Obtener ruta de transporte para una fecha específica"""
        try:
            rutas = self.__carelink_session.query(CronogramaTransporte).join(
                CronogramaAsistenciaPacientes
            ).join(
                CronogramaAsistencia
            ).join(
                User
            ).filter(
                CronogramaAsistencia.fecha == fecha
            ).all()
            
            return [
                {
                    "id_transporte": ruta.id_transporte,
                    "id_cronograma_paciente": ruta.id_cronograma_paciente,
                    "nombres": ruta.cronograma_paciente.usuario.nombres,
                    "apellidos": ruta.cronograma_paciente.usuario.apellidos,
                    "n_documento": ruta.cronograma_paciente.usuario.n_documento,
                    "direccion_recogida": ruta.direccion_recogida,
                    "direccion_entrega": ruta.direccion_entrega,
                    "hora_recogida": ruta.hora_recogida,
                    "hora_entrega": ruta.hora_entrega,
                    "estado": ruta.estado,
                    "observaciones": ruta.observaciones
                }
                for ruta in rutas
            ]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener ruta diaria: {str(e)}"
            )

    def get_transporte_paciente(self, id_cronograma_paciente: int) -> CronogramaTransporte:
        """Obtener transporte de un paciente específico"""
        try:
            # Verificar que el paciente existe
            self._get_cronograma_paciente_by_id(id_cronograma_paciente)
            
            transporte = self.__carelink_session.query(CronogramaTransporte).filter(
                CronogramaTransporte.id_cronograma_paciente == id_cronograma_paciente
            ).first()
            
            if not transporte:
                raise EntityNotFoundError(f"No se encontró transporte para el paciente {id_cronograma_paciente}")
            
            return transporte
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener transporte del paciente: {str(e)}"
            )

    def _get_transporte_by_id(self, id_transporte: int) -> CronogramaTransporte:
        """Obtener transporte por ID"""
        transporte = self.__carelink_session.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_transporte == id_transporte
        ).first()
        
        if not transporte:
            raise EntityNotFoundError(f"Transporte con ID {id_transporte} no encontrado")
        
        return transporte

    def create_factura(self, factura_data):
        # 1. Validar que no exista ya una factura para el contrato
        detalles = factura_data.get('detalles', [])
        impuestos = factura_data.get('impuestos', 0)
        descuentos = factura_data.get('descuentos', 0)
        # Si no se reciben detalles, generarlos automáticamente
        if not detalles:
            servicios = self.__carelink_session.query(ServiciosPorContrato).filter(
                ServiciosPorContrato.id_contrato == factura_data['id_contrato']
            ).all()
            for servicio in servicios:
                fechas_servicio = self.__carelink_session.query(FechasServicio).filter_by(
                    id_servicio_contratado=servicio.id_servicio_contratado
                ).all()
                cantidad = len(fechas_servicio)
                tarifa = self.__carelink_session.query(TarifasServicioPorAnio).filter_by(
                    id_servicio=servicio.id_servicio,
                    anio=int(str(factura_data['fecha_emision'])[:4])
                ).first()
                valor_unitario = tarifa.precio_por_dia if tarifa else 0
                nombre_servicio = self.__carelink_session.query(Servicios).filter_by(
                    id_servicio=servicio.id_servicio
                ).first().nombre
                detalles.append({
                    'id_servicio_contratado': servicio.id_servicio_contratado,
                    'cantidad': cantidad,
                    'valor_unitario': valor_unitario,
                    'subtotal_linea': cantidad * valor_unitario,
                    'impuestos_linea': impuestos,
                    'descuentos_linea': descuentos,
                    'descripcion_servicio': nombre_servicio
                })
        # 2. Calcular el total de la factura
        subtotal = sum([d['subtotal_linea'] for d in detalles])
        impuestos_total = sum([d.get('impuestos_linea', 0) for d in detalles])
        descuentos_total = sum([d.get('descuentos_linea', 0) for d in detalles])
        total_factura = subtotal + impuestos_total - descuentos_total
        # 3. Crear la factura SIN numero_factura
        factura = Facturas(
            id_contrato=factura_data['id_contrato'],
            fecha_emision=factura_data['fecha_emision'],
            fecha_vencimiento=factura_data.get('fecha_vencimiento'),
            subtotal=subtotal,
            impuestos=impuestos_total,
            descuentos=descuentos_total,
            total_factura=total_factura,
            estado_factura='PENDIENTE',
            observaciones=factura_data.get('observaciones', None)
        )
        self.__carelink_session.add(factura)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(factura)

        # 4. Generar numero_factura basado en id_factura (relleno de ceros a la izquierda)
        numero_factura = str(factura.id_factura).zfill(4)
        factura.numero_factura = numero_factura
        self.__carelink_session.commit()
        self.__carelink_session.refresh(factura)

        # 5. Asociar detalles
        for detalle in detalles:
            detalle_factura = DetalleFactura(
                id_factura=factura.id_factura,
                id_servicio_contratado=detalle['id_servicio_contratado'],
                cantidad=detalle['cantidad'],
                valor_unitario=detalle['valor_unitario'],
                subtotal_linea=detalle.get('subtotal_linea', detalle['cantidad']*detalle['valor_unitario']),
                impuestos_linea=detalle.get('impuestos_linea', 0),
                descuentos_linea=detalle.get('descuentos_linea', 0),
                descripcion_servicio=detalle.get('descripcion_servicio', None)
            )
            self.__carelink_session.add(detalle_factura)

        # 6. Asociar pagos
        for pago in factura_data.get('pagos', []):
            pago_obj = Pagos(
                id_factura=factura.id_factura,
                id_metodo_pago=pago['id_metodo_pago'],
                id_tipo_pago=pago['id_tipo_pago'],
                fecha_pago=pago['fecha_pago'],
                valor=pago['valor']
            )
            self.__carelink_session.add(pago_obj)

        self.__carelink_session.commit()
        self.__carelink_session.refresh(factura)
        return factura

    def actualizar_estados_contratos_finalizados(self):
        """
        Actualiza el estado de todos los contratos cuya fecha_fin sea menor a hoy y que estén en estado ACTIVO, cambiándolos a FINALIZADO.
        """
        from datetime import date
        contratos = self.__carelink_session.query(Contratos).filter(
            Contratos.estado == 'ACTIVO',
            Contratos.fecha_fin != None,
            Contratos.fecha_fin < date.today()
        ).all()
        for contrato in contratos:
            contrato.estado = 'FINALIZADO'
        if contratos:
            self.__carelink_session.commit()

    def get_all_service_rates(self) -> List[TarifasServicioPorAnio]:
        """Obtener todas las tarifas de servicios por año"""
        try:
            tarifas = self.__carelink_session.query(TarifasServicioPorAnio).join(
                Servicios, TarifasServicioPorAnio.id_servicio == Servicios.id_servicio
            ).all()
            return tarifas
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener tarifas de servicios: {str(e)}"
            )

    def update_service_rates(self, tarifas_data: List[dict]) -> List[TarifasServicioPorAnio]:
        """Actualizar múltiples tarifas de servicios por año"""
        try:
            updated_tarifas = []
            
            for tarifa_data in tarifas_data:
                # Buscar la tarifa existente
                tarifa = self.__carelink_session.query(TarifasServicioPorAnio).filter(
                    TarifasServicioPorAnio.id == tarifa_data['id']
                ).first()
                
                if not tarifa:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Tarifa con ID {tarifa_data['id']} no encontrada"
                    )
                
                # Verificar que el servicio existe
                servicio = self.__carelink_session.query(Servicios).filter(
                    Servicios.id_servicio == tarifa_data['id_servicio']
                ).first()
                
                if not servicio:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Servicio con ID {tarifa_data['id_servicio']} no encontrado"
                    )
                
                # Actualizar los campos
                tarifa.id_servicio = tarifa_data['id_servicio']
                tarifa.anio = tarifa_data['anio']
                tarifa.precio_por_dia = float(tarifa_data['precio_por_dia'])
                
                updated_tarifas.append(tarifa)
            
            self.__carelink_session.commit()
            
            # Refrescar todas las tarifas actualizadas
            for tarifa in updated_tarifas:
                self.__carelink_session.refresh(tarifa)
            
            return updated_tarifas
            
        except SQLAlchemyError as e:
            self.__carelink_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar tarifas de servicios: {str(e)}"
            )

    def get_complete_factura_data_for_pdf(self, factura_id: int) -> dict:
        """
        Obtiene todos los datos necesarios para generar el PDF de la factura
        """
        try:
            # 1. Obtener la factura
            factura = self._get_factura_by_id(factura_id)
            if not factura:
                return None
            
            # 2. Obtener el contrato asociado
            contrato = self._get_contract_by_id(factura.id_contrato)
            
            # 3. Obtener el usuario asociado al contrato
            usuario = self._get_user_by_id(contrato.id_usuario)
            
            # 4. Obtener los servicios incluidos en la factura
            servicios = self._get_contract_services(factura.id_contrato)
            
            # 5. Obtener los pagos asociados a la factura
            pagos = self._get_pagos_by_factura(factura_id)
            
            # 6. Obtener el cronograma de días agendados
            cronograma = self._get_cronograma_by_contrato_and_user(
                contrato.id_contrato, 
                usuario.id_usuario
            )
            
            # 7. Calcular totales
            total_pagado = sum(pago.valor for pago in pagos)
            saldo_pendiente = factura.total_factura - total_pagado
            
            return {
                "factura": factura,
                "contrato": contrato,
                "usuario": usuario,
                "servicios": servicios,
                "pagos": pagos,
                "cronograma": cronograma,
                "total_pagado": total_pagado,
                "saldo_pendiente": saldo_pendiente
            }
            
        except Exception as e:
            print(f"Error obteniendo datos de factura {factura_id}: {str(e)}")
            return None

    def generate_factura_pdf(self, factura_data: dict) -> bytes:
        """
        Genera el PDF de la factura con toda la información
        """
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from io import BytesIO
        from datetime import datetime
        
        # Crear el buffer para el PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20
        )
        normal_style = styles['Normal']
        
        # --- CABECERA CON LOGO Y DATOS PRINCIPALES ---
        import os
        from reportlab.platypus import Image
        logo_path = os.path.join(os.path.dirname(__file__), '../static/psicoabuelosPDF.jpeg')
        if os.path.exists(logo_path):
            img = Image(logo_path, width=180, height=60)
            img.hAlign = 'LEFT'
            story.append(img)
            story.append(Spacer(1, 10))
        
        # Título con número de factura y contrato
        story.append(Paragraph(f"<b>Factura N° {factura_data.get('numero_factura', '')}</b>   |   <b>Contrato N° {factura_data.get('id_contrato', '')}</b>", ParagraphStyle('Title', parent=title_style, fontSize=18, textColor=colors.HexColor('#4B0082'))))
        story.append(Spacer(1, 20))

        # Datos de la factura
        factura = factura_data["factura"]
        story.append(Paragraph("INFORMACIÓN DE LA FACTURA", subtitle_style))
        
        factura_info = [
            ["Número de Factura:", factura.numero_factura or f"F-{factura.id_factura}"],
            ["Fecha de Emisión:", factura.fecha_emision.strftime("%d/%m/%Y")],
            ["Fecha de Vencimiento:", factura.fecha_vencimiento.strftime("%d/%m/%Y") if factura.fecha_vencimiento else "N/A"],
            ["Estado:", factura.estado_factura or "PENDIENTE"],
            ["Subtotal:", f"$ {factura.subtotal:,.0f}"],
            ["Impuestos:", f"$ {factura.impuestos:,.0f}"],
            ["Descuentos:", f"$ {factura.descuentos:,.0f}"],
            ["Total:", f"$ {factura.total_factura:,.0f}"],
        ]
        
        factura_table = Table(factura_info, colWidths=[2*inch, 3*inch])
        factura_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(factura_table)
        story.append(Spacer(1, 20))
        
        # Datos del usuario
        usuario = factura_data["usuario"]
        story.append(Paragraph("DATOS DEL CLIENTE", subtitle_style))
        
        usuario_info = [
            ["Nombre Completo:", f"{usuario.nombres} {usuario.apellidos}"],
            ["Documento:", usuario.n_documento or "N/A"],
            ["Dirección:", usuario.direccion or "N/A"],
            ["Teléfono:", usuario.telefono or "N/A"],
            ["Email:", usuario.email or "N/A"],
        ]
        
        usuario_table = Table(usuario_info, colWidths=[2*inch, 3*inch])
        usuario_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(usuario_table)
        story.append(Spacer(1, 20))
        
        # Datos del contrato
        contrato = factura_data["contrato"]
        story.append(Paragraph("DATOS DEL CONTRATO", subtitle_style))
        
        contrato_info = [
            ["ID Contrato:", str(contrato.id_contrato)],
            ["Tipo de Contrato:", contrato.tipo_contrato],
            ["Fecha de Inicio:", contrato.fecha_inicio.strftime("%d/%m/%Y")],
            ["Fecha de Fin:", contrato.fecha_fin.strftime("%d/%m/%Y")],
        ]
        
        contrato_table = Table(contrato_info, colWidths=[2*inch, 3*inch])
        contrato_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(contrato_table)
        story.append(Spacer(1, 20))
        
        # Servicios incluidos
        servicios = factura_data["servicios"]
        story.append(Paragraph("SERVICIOS INCLUIDOS", subtitle_style))
        
        if servicios:
            servicios_data = [["Servicio", "Descripción", "Precio/Día", "Días", "Total"]]
            for servicio in servicios:
                # Obtener las fechas de servicio usando el método correcto
                fechas_servicio = self._get_service_dates(servicio)
                dias_servicio = len(fechas_servicio)
                total_servicio = float(servicio.precio_por_dia) * dias_servicio
                servicios_data.append([
                    servicio.servicio.nombre if hasattr(servicio, 'servicio') and servicio.servicio else f"Servicio #{servicio.id_servicio_contratado}",
                    servicio.descripcion,
                    f"$ {servicio.precio_por_dia:,.0f}",
                    str(dias_servicio),
                    f"$ {total_servicio:,.0f}"
                ])
            
            servicios_table = Table(servicios_data, colWidths=[1*inch, 2*inch, 1*inch, 0.5*inch, 1*inch])
            servicios_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ]))
            story.append(servicios_table)
        else:
            story.append(Paragraph("No hay servicios registrados", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Pagos realizados
        pagos = factura_data["pagos"]
        story.append(Paragraph("PAGOS REALIZADOS", subtitle_style))
        
        if pagos:
            pagos_data = [["Fecha", "Método", "Tipo", "Valor"]]
            for pago in pagos:
                metodo_pago = self._get_payment_method_name(pago.id_metodo_pago)
                tipo_pago = self._get_payment_type_name(pago.id_tipo_pago)
                pagos_data.append([
                    pago.fecha_pago.strftime("%d/%m/%Y"),
                    metodo_pago,
                    tipo_pago,
                    f"$ {pago.valor:,.0f}"
                ])
            
            pagos_table = Table(pagos_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch])
            pagos_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ]))
            story.append(pagos_table)
        else:
            story.append(Paragraph("No hay pagos registrados", normal_style))
        
        story.append(Spacer(1, 20))
        
        # --- CRONOGRAMA SIMPLIFICADO ---
        cronograma = factura_data.get("cronograma", [])
        story.append(Paragraph("CRONOGRAMA DE SERVICIOS", subtitle_style))
        if cronograma:
            cronograma_data = [["Fecha", "Transporte"]]
            for item in cronograma:
                # Corregir acceso: usar atributos en vez de .get()
                fecha = getattr(item, 'fecha', None) if not isinstance(item, dict) else item.get('fecha')
                transporte = getattr(item, 'transporte', None) if not isinstance(item, dict) else item.get('transporte')
                if transporte is True or (isinstance(transporte, str) and transporte.lower().startswith("sí")):
                    transporte_str = "Sí - PENDIENTE"
                else:
                    transporte_str = "No"
                cronograma_data.append([
                    fecha,
                    transporte_str
                ])
            cronograma_table = Table(cronograma_data, colWidths=[1.5*inch, 1.5*inch])
            cronograma_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ]))
            story.append(cronograma_table)
        else:
            story.append(Paragraph("No hay cronograma registrado", normal_style))
        story.append(Spacer(1, 20))
        
        # Resumen de pagos
        story.append(Paragraph("RESUMEN DE PAGOS", subtitle_style))
        
        total_pagado = factura_data["total_pagado"]
        saldo_pendiente = factura_data["saldo_pendiente"]
        
        resumen_data = [
            ["Total Factura:", f"$ {factura.total_factura:,.0f}"],
            ["Total Pagado:", f"$ {total_pagado:,.0f}"],
            ["Saldo Pendiente:", f"$ {saldo_pendiente:,.0f}"],
        ]
        
        resumen_table = Table(resumen_data, colWidths=[2*inch, 2*inch])
        resumen_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(resumen_table)
        
        # Observaciones
        if factura.observaciones:
            story.append(Spacer(1, 20))
            story.append(Paragraph("OBSERVACIONES", subtitle_style))
            story.append(Paragraph(factura.observaciones, normal_style))
        
        # Pie de página
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            ParagraphStyle('Footer', parent=normal_style, fontSize=8, alignment=TA_CENTER)
        ))
        
        # Generar el PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes

    def _get_payment_method_name(self, id_metodo_pago: int) -> str:
        """Obtiene el nombre del método de pago"""
        try:
            metodo = self.__carelink_session.query(MetodoPago).filter(
                MetodoPago.id_metodo_pago == id_metodo_pago
            ).first()
            return metodo.nombre if metodo else f"Método #{id_metodo_pago}"
        except:
            return f"Método #{id_metodo_pago}"

    def _get_payment_type_name(self, id_tipo_pago: int) -> str:
        """Obtiene el nombre del tipo de pago"""
        try:
            tipo = self.__carelink_session.query(TipoPago).filter(
                TipoPago.id_tipo_pago == id_tipo_pago
            ).first()
            return tipo.nombre if tipo else f"Tipo #{id_tipo_pago}"
        except:
            return f"Tipo #{id_tipo_pago}"

    def _get_factura_by_id(self, factura_id: int):
        """Obtiene una factura por ID"""
        try:
            return self.__carelink_session.query(Facturas).filter(
                Facturas.id_factura == factura_id
            ).first()
        except:
            return None

    def _get_pagos_by_factura(self, factura_id: int):
        """Obtiene los pagos de una factura"""
        try:
            return self.__carelink_session.query(Pagos).filter(
                Pagos.id_factura == factura_id
            ).all()
        except:
            return []

    def _get_cronograma_by_contrato_and_user(self, contrato_id: int, usuario_id: int):
        """Obtiene el cronograma de un contrato y usuario específicos"""
        try:
            from app.models.attendance_schedule import CronogramaAsistencia
            return self.__carelink_session.query(CronogramaAsistencia).join(
                CronogramaAsistencia.pacientes
            ).filter(
                CronogramaAsistenciaPacientes.id_contrato == contrato_id,
                CronogramaAsistenciaPacientes.id_usuario == usuario_id
            ).all()
        except:
            return []

def get_bill_payments_total(db, id_factura: int) -> float:
    """
    Retorna el total de pagos asociados a una factura
    """
    from app.models.contracts import Pagos
    pagos = db.query(Pagos).filter(Pagos.id_factura == id_factura).all()
    total = sum(float(pago.valor) for pago in pagos)
    return total
