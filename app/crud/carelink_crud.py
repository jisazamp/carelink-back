from app.dto.v1.request.contracts import ContratoCreateDTO
from app.dto.v1.request.payment_method import CreateUserPaymentRequestDTO
from app.dto.v1.response.contracts import ContratoResponseDTO, ServicioContratoDTO, FechaServicioDTO
from app.exceptions.exceptions_classes import EntityNotFoundError
from app.models.activities import ActividadesGrupales, TipoActividad
from app.models.activity_users import ActividadesUsuarios
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
from app.models.home_visit import VisitasDomiciliarias, VisitasDomiciliariasPorProfesional
from boto3 import client
from botocore.exceptions import NoCredentialsError
from datetime import date, datetime
from fastapi import HTTPException, UploadFile, status
from passlib.context import CryptContext
from sqlalchemy import select, delete
from sqlalchemy.orm import Session, joinedload
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
        # fecha_visita y hora_visita se dejan como NULL para que el usuario las complete
        visita_data = {
            "id_usuario": user_id,
            "id_contrato": None,  # Se asignará cuando se cree el contrato
            "fecha_visita": None,  # NULL - debe ser completado por el usuario
            "hora_visita": None,   # NULL - debe ser completado por el usuario
            "estado_visita": "PENDIENTE",
            "direccion_visita": user_data.get("direccion", ""),
            "telefono_visita": user_data.get("telefono", ""),
            "valor_dia": 0.00,
            "observaciones": f"Visita domiciliaria creada automáticamente para usuario {user_id} - Pendiente de programación",
            "fecha_creacion": datetime.utcnow(),
            "fecha_actualizacion": datetime.utcnow()
        }

        visita = VisitasDomiciliarias(**visita_data)
        self.__carelink_session.add(visita)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(visita)

        # Intentar asignar un profesional por defecto si hay profesionales disponibles
        try:
            profesionales = self._get_professionals()
            if profesionales:
                # Tomar el primer profesional activo disponible
                profesional_activo = next(
                    (p for p in profesionales if p.estado == "Activo"), 
                    profesionales[0]
                )
                
                # Crear la asignación del profesional
                asignacion = VisitasDomiciliariasPorProfesional(
                    id_visitadomiciliaria=visita.id_visitadomiciliaria,
                    id_profesional=profesional_activo.id_profesional,
                    estado_asignacion="ACTIVA",
                    fecha_asignacion=datetime.utcnow()
                )
                self.__carelink_session.add(asignacion)
                self.__carelink_session.commit()
        except Exception as e:
            # Si hay algún error al asignar el profesional, no fallar la creación de la visita
            print(f"⚠️ No se pudo asignar profesional por defecto: {e}")

        return visita

    def _check_existing_acudiente(self, user_id: int) -> bool:
        """Check if user already has an acudiente (family member with acudiente=1)"""
        existing_acudiente = self.__carelink_session.query(FamilyMember).join(
            FamiliaresYAcudientesPorUsuario,
            FamilyMember.id_acudiente == FamiliaresYAcudientesPorUsuario.id_acudiente
        ).filter(
            FamiliaresYAcudientesPorUsuario.id_usuario == user_id,
            FamilyMember.acudiente == True,
            FamilyMember.is_deleted == False
        ).first()
        
        return existing_acudiente is not None

    def save_family_member(self, id: int, kinship, family_member: FamilyMember):
        user = self._get_user_by_id(id)
        kinship_string = kinship.dict()["parentezco"]
        
        # Check if trying to mark as acudiente and user already has one
        if family_member.acudiente and self._check_existing_acudiente(id):
            raise ValueError("El usuario ya tiene un acudiente registrado. Solo puede tener un acudiente por usuario.")
        
        # If marking as acudiente, unmark any existing acudiente
        if family_member.acudiente:
            existing_acudiente = self.__carelink_session.query(FamilyMember).join(
                FamiliaresYAcudientesPorUsuario,
                FamilyMember.id_acudiente == FamiliaresYAcudientesPorUsuario.id_acudiente
            ).filter(
                FamiliaresYAcudientesPorUsuario.id_usuario == id,
                FamilyMember.acudiente == True,
                FamilyMember.is_deleted == False
            ).first()
            
            if existing_acudiente:
                existing_acudiente.acudiente = False
        
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
        
        # Actualizar los campos de localización del usuario SOLO si es acudiente
        if family_member.acudiente:
            if family_member.telefono:
                user.telefono = family_member.telefono
            if family_member.email:
                user.email = family_member.email
            if family_member.direccion:
                user.direccion = family_member.direccion
            
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
        # Obtener el usuario para actualizar sus campos de localización
        user = self._get_user_by_id(user_id)
        
        # Check if trying to mark as acudiente and user already has one (excluding current family member)
        if family_member.acudiente and not db_family_member.acudiente:
            # Solo verificar si ya existe otro acudiente cuando se está convirtiendo en acudiente
            existing_acudiente = self.__carelink_session.query(FamilyMember).join(
                FamiliaresYAcudientesPorUsuario,
                FamilyMember.id_acudiente == FamiliaresYAcudientesPorUsuario.id_acudiente
            ).filter(
                FamiliaresYAcudientesPorUsuario.id_usuario == user_id,
                FamilyMember.acudiente == True,
                FamilyMember.is_deleted == False,
                FamilyMember.id_acudiente != db_family_member.id_acudiente
            ).first()
            
            # Si existe otro acudiente, desactivarlo antes de activar el actual
            if existing_acudiente:
                existing_acudiente.acudiente = False
        
        # Check if this family member was previously an acudiente and is being unmarked
        was_previous_acudiente = db_family_member.acudiente and not family_member.acudiente
        
        for key, value in family_member.__dict__.items():
            if key != "_sa_instance_state" and value is not None:
                if hasattr(db_family_member, key):
                    setattr(db_family_member, key, value)
        
        # Actualizar los campos de localización del usuario SOLO si es acudiente
        if family_member.acudiente:
            if family_member.telefono:
                user.telefono = family_member.telefono
            if family_member.email:
                user.email = family_member.email
            if family_member.direccion:
                user.direccion = family_member.direccion
        # Si era acudiente y ahora no lo es, limpiar los datos de localización del usuario
        elif was_previous_acudiente:
            user.telefono = None
            user.email = None
            user.direccion = None
            
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

    def update_user_medical_record_simplified(
        self,
        user_id: int,
        record_id: int,
        update_data: dict,
    ) -> MedicalRecord:
        """Actualizar solo el registro principal de la historia clínica sin medicamentos, cuidados, etc."""
        self._get_user_by_id(user_id)
        db_record = self._get_medical_record_by_id(record_id)

        for key, value in update_data.items():
            if hasattr(db_record, key):
                setattr(db_record, key, value)

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

    def get_payments_by_factura(self, factura_id: int) -> list[Pagos]:
        return self.__carelink_session.execute(
            select(Pagos).where(Pagos.id_factura == factura_id)
        ).scalars().all()

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
        # Intentar obtener la tarifa del servicio, si no existe usar el precio del servicio contratado
        service_rate = self._get_service_rate(service.id_servicio, contract_start_year)
        if service_rate is None:
            # Si no hay tarifa configurada, usar el precio del servicio contratado
            # Para servicios por contrato, asumimos cantidad = 1 (un día de servicio)
            return float(service.precio_por_dia)
        # Para servicios por contrato, asumimos cantidad = 1 (un día de servicio)
        return service_rate.precio_por_dia

    def _calculate_contract_bill_total(self, contract_id: int) -> float:
        services = self._get_contract_services(contract_id)
        total = 0.0
        
        for service in services:
            # Obtener las fechas de servicio para este servicio contratado
            fechas_servicio = self._get_service_dates(service)
            num_fechas = len(fechas_servicio)
            
            # Calcular el total para este servicio: precio por día * número de fechas
            precio_por_dia = float(service.precio_por_dia)
            total_servicio = precio_por_dia * num_fechas
            total += total_servicio
            
        
        return total

    def calculate_partial_bill(
        self, service_ids: list[int], quantities: list[int], year: int
    ) -> float:
        total = 0
        for service_id, quantity in zip(service_ids, quantities):
            rate = self._get_service_rate(service_id, year)
            if rate is None:
                # Si no hay tarifa configurada, usar un precio por defecto o lanzar error
                raise ValueError(f"No se encontró tarifa configurada para el servicio {service_id} en el año {year}")
            total += rate.precio_por_dia * quantity
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
        )
        self.__carelink_session.add(contract)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(contract)
        
        # Crear servicios por contrato
        servicios_por_contrato = []
        for servicio_data in contract_data.servicios:
            servicio_contratado = ServiciosPorContrato(
                id_contrato=contract.id_contrato,
                id_servicio=servicio_data.id_servicio,
                fecha=servicio_data.fecha,
                descripcion=servicio_data.descripcion,
                precio_por_dia=servicio_data.precio_por_dia
            )
            self.__carelink_session.add(servicio_contratado)
            self.__carelink_session.commit()
            self.__carelink_session.refresh(servicio_contratado)
            
            # Crear fechas de servicio
            for fecha_servicio_data in servicio_data.fechas_servicio:
                fecha_servicio = FechasServicio(
                    id_servicio_contratado=servicio_contratado.id_servicio_contratado,
                    fecha=fecha_servicio_data.fecha
                )
                self.__carelink_session.add(fecha_servicio)
            
            self.__carelink_session.commit()
            
            # Agregar a la lista de servicios por contrato
            servicios_por_contrato.append({
                'id_servicio_contratado': servicio_contratado.id_servicio_contratado,
                'id_servicio': servicio_contratado.id_servicio,
                'fecha': servicio_contratado.fecha,
                'descripcion': servicio_contratado.descripcion,
                'precio_por_dia': servicio_contratado.precio_por_dia
            })
        
        return {
            'contrato': contract,
            'servicios_por_contrato': servicios_por_contrato
        }

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

    def _get_user_guardian_info(self, user_id: int) -> dict:
        """Obtener información del acudiente principal del usuario"""
        try:
            # Obtener el primer acudiente asociado al usuario
            guardian_relation = self.__carelink_session.execute(
                select(FamiliaresYAcudientesPorUsuario)
                .options(joinedload(FamiliaresYAcudientesPorUsuario.acudiente))
                .where(FamiliaresYAcudientesPorUsuario.id_usuario == user_id)
                .limit(1)
            ).scalar_one_or_none()
            
            if guardian_relation and guardian_relation.acudiente:
                guardian = guardian_relation.acudiente
                return {
                    "nombre_completo": f"{guardian.nombres} {guardian.apellidos}",
                    "telefono": guardian.telefono or "No especificado",
                    "documento": guardian.n_documento or "No especificado",
                    "parentesco": guardian_relation.parentesco or "No especificado"
                }
            else:
                return {
                    "nombre_completo": "No especificado",
                    "telefono": "No especificado", 
                    "documento": "No especificado",
                    "parentesco": "No especificado"
                }
        except Exception as e:
            print(f"Error obteniendo información del acudiente: {e}")
            return {
                "nombre_completo": "No especificado",
                "telefono": "No especificado",
                "documento": "No especificado", 
                "parentesco": "No especificado"
            }

    def _get_service_price_by_name(self, service_name: str, year: int) -> float:
        """Obtener precio por día de un servicio basado en su nombre"""
        try:
            # Buscar el servicio por nombre
            service = self.__carelink_session.execute(
                select(Servicios).where(Servicios.nombre.ilike(f"%{service_name}%"))
            ).scalar_one_or_none()
            
            if service:
                # Obtener la tarifa para ese servicio y año
                rate = self._get_service_rate(service.id_servicio, year)
                if rate:
                    return float(rate.precio_por_dia)
            
            return 0.0
        except Exception as e:
            print(f"Error obteniendo precio del servicio {service_name}: {e}")
            return 0.0

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
            select(FamiliaresYAcudientesPorUsuario)
            .options(joinedload(FamiliaresYAcudientesPorUsuario.acudiente))
            .where(
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
        # Primero obtener el id_historiaclinica del usuario
        medical_record = self._get_user_medical_record_by_user_id(user_id)
        if not medical_record:
            return []
        
        # Luego buscar los reportes clínicos asociados a esa historia clínica
        return self.__carelink_session.execute(
            select(ReportesClinicos).where(ReportesClinicos.id_historiaclinica == medical_record.id_historiaclinica)
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
                EvolucionesClinicas.id_TipoReporte == evolution_id
            )
        ).scalar_one_or_none()
        if not evolution:
            raise EntityNotFoundError(f"Evolución clínica con ID {evolution_id} no encontrada")
        return evolution

    def _get_activities(self) -> List[ActividadesGrupales]:
        return self.__carelink_session.execute(select(ActividadesGrupales)).scalars().all()

    def _get_activity_by_id(self, id: int) -> ActividadesGrupales:
        activity = self.__carelink_session.execute(
            select(ActividadesGrupales).where(ActividadesGrupales.id == id)
        ).scalar_one_or_none()
        if not activity:
            raise EntityNotFoundError(f"Actividad con ID {id} no encontrada")
        return activity

    def _get_activity_types(self) -> List[TipoActividad]:
        return self.__carelink_session.execute(select(TipoActividad)).scalars().all()

    def _get_upcoming_activities(self) -> List[ActividadesGrupales]:
        return self.__carelink_session.execute(
            select(ActividadesGrupales)
            .where(ActividadesGrupales.fecha >= date.today())
            .order_by(ActividadesGrupales.fecha.asc())
            .limit(10)
        ).scalars().all()

    def get_activity_with_users(self, activity_id: int) -> dict:
        """Obtener una actividad con sus usuarios asignados"""
        from app.dto.v1.response.activity_users import ActivityWithUsersDTO, ActivityUserDTO
        
        # Obtener la actividad
        activity = self._get_activity_by_id(activity_id)
        
        # Obtener usuarios asignados
        usuarios_asignados = self.__carelink_session.execute(
            select(ActividadesUsuarios, User)
            .join(User, ActividadesUsuarios.id_usuario == User.id_usuario)
            .where(ActividadesUsuarios.id_actividad == activity_id)
        ).all()
        
        # Construir la respuesta
        usuarios_dto = []
        for au, user in usuarios_asignados:
            usuarios_dto.append(ActivityUserDTO(
                id=au.id,
                id_usuario=au.id_usuario,
                id_actividad=au.id_actividad,
                fecha_asignacion=au.fecha_asignacion,
                estado_participacion=au.estado_participacion,
                observaciones=au.observaciones,
                fecha_creacion=au.fecha_creacion,
                fecha_actualizacion=au.fecha_actualizacion,
                nombres=user.nombres,
                apellidos=user.apellidos,
                n_documento=user.n_documento
            ))
        
        return ActivityWithUsersDTO(
            id=activity.id,
            nombre=activity.nombre,
            descripcion=activity.descripcion,
            fecha=activity.fecha,
            duracion=activity.duracion,
            comentarios=activity.comentarios,
            id_profesional=activity.id_profesional,
            id_tipo_actividad=activity.id_tipo_actividad,
            profesional_nombres=activity.profesional.nombres if activity.profesional else None,
            profesional_apellidos=activity.profesional.apellidos if activity.profesional else None,
            tipo_actividad=activity.tipo_actividad.tipo if activity.tipo_actividad else None,
            usuarios_asignados=usuarios_dto,
            total_usuarios=len(usuarios_dto)
        )

    def get_users_for_activity_date(self, activity_date: date) -> List[dict]:
        """Obtener usuarios agendados en el cronograma para una fecha específica"""
        from app.dto.v1.response.activity_users import UserForActivityDTO
        
        # Obtener solo los usuarios que están agendados en el cronograma para esa fecha
        usuarios_cronograma = self.__carelink_session.execute(
            select(User, CronogramaAsistenciaPacientes)
            .join(CronogramaAsistenciaPacientes, User.id_usuario == CronogramaAsistenciaPacientes.id_usuario)
            .join(CronogramaAsistencia, CronogramaAsistenciaPacientes.id_cronograma == CronogramaAsistencia.id_cronograma)
            .where(CronogramaAsistencia.fecha == activity_date)
            .where(User.is_deleted == False)
        ).all()
        
        # Construir la respuesta solo con usuarios agendados
        usuarios_dto = []
        for user, cap in usuarios_cronograma:
            usuarios_dto.append(UserForActivityDTO(
                id_usuario=user.id_usuario,
                nombres=user.nombres,
                apellidos=user.apellidos,
                n_documento=user.n_documento,
                telefono=user.telefono,
                email=user.email,
                fecha_nacimiento=user.fecha_nacimiento,
                genero=user.genero,
                estado=user.estado,
                tiene_cronograma_fecha=True,  # Todos los usuarios devueltos tienen cronograma
                estado_asistencia=cap.estado_asistencia.value if cap.estado_asistencia else None
            ))
        
        return usuarios_dto

    def assign_users_to_activity(self, activity_id: int, user_ids: List[int], estado_participacion: str = "PENDIENTE", observaciones: str = None) -> List[ActividadesUsuarios]:
        """Asignar usuarios a una actividad"""
        # Verificar que la actividad existe
        activity = self._get_activity_by_id(activity_id)
        
        # Crear las asignaciones
        asignaciones = []
        for user_id in user_ids:
            # Verificar que el usuario existe
            user = self.__carelink_session.execute(
                select(User).where(User.id_usuario == user_id)
            ).scalar_one_or_none()
            
            if not user:
                raise ValueError(f"Usuario con ID {user_id} no encontrado")
            
            # Verificar si ya existe la asignación
            existing = self.__carelink_session.execute(
                select(ActividadesUsuarios)
                .where(ActividadesUsuarios.id_actividad == activity_id)
                .where(ActividadesUsuarios.id_usuario == user_id)
            ).scalar_one_or_none()
            
            if existing:
                # Actualizar la asignación existente
                existing.estado_participacion = estado_participacion
                if observaciones:
                    existing.observaciones = observaciones
                asignaciones.append(existing)
            else:
                # Crear nueva asignación
                nueva_asignacion = ActividadesUsuarios(
                    id_actividad=activity_id,
                    id_usuario=user_id,
                    estado_participacion=estado_participacion,
                    observaciones=observaciones
                )
                self.__carelink_session.add(nueva_asignacion)
                asignaciones.append(nueva_asignacion)
        
        self.__carelink_session.commit()
        return asignaciones

    def remove_users_from_activity(self, activity_id: int, user_ids: List[int]) -> bool:
        """Remover usuarios de una actividad"""
        # Eliminar las asignaciones
        deleted = self.__carelink_session.execute(
            delete(ActividadesUsuarios)
            .where(ActividadesUsuarios.id_actividad == activity_id)
            .where(ActividadesUsuarios.id_usuario.in_(user_ids))
        )
        
        self.__carelink_session.commit()
        return deleted.rowcount > 0

    def update_user_activity_status(self, activity_user_id: int, estado_participacion: str, observaciones: str = None) -> ActividadesUsuarios:
        """Actualizar el estado de participación de un usuario en una actividad"""
        activity_user = self.__carelink_session.execute(
            select(ActividadesUsuarios)
            .where(ActividadesUsuarios.id == activity_user_id)
        ).scalar_one_or_none()
        
        if not activity_user:
            raise ValueError(f"Asignación de actividad con ID {activity_user_id} no encontrada")
        
        activity_user.estado_participacion = estado_participacion
        if observaciones:
            activity_user.observaciones = observaciones
        
        self.__carelink_session.commit()
        return activity_user

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

    def get_all_service_rates(self):
        """
        Devuelve todas las tarifas de servicios por año.
        """
        return self.__carelink_session.query(TarifasServicioPorAnio).all()

    def update_service_rates(self, tarifas_data: List[dict]) -> List[TarifasServicioPorAnio]:
        """
        Actualiza múltiples tarifas de servicios por año.
        
        Args:
            tarifas_data: Lista de diccionarios con los datos de las tarifas a actualizar
                Cada diccionario debe contener: id, id_servicio, anio, precio_por_dia
        
        Returns:
            Lista de objetos TarifasServicioPorAnio actualizados
        """
        updated_tarifas = []
        
        for tarifa_data in tarifas_data:
            # Buscar la tarifa existente por ID
            tarifa = self.__carelink_session.query(TarifasServicioPorAnio).filter(
                TarifasServicioPorAnio.id == tarifa_data['id']
            ).first()
            
            if not tarifa:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tarifa con ID {tarifa_data['id']} no encontrada"
                )
            
            # Actualizar los campos
            tarifa.id_servicio = tarifa_data['id_servicio']
            tarifa.anio = tarifa_data['anio']
            tarifa.precio_por_dia = tarifa_data['precio_por_dia']
            
            updated_tarifas.append(tarifa)
        
        # Confirmar todos los cambios
        self.__carelink_session.commit()
        
        # Refrescar los objetos para obtener los datos actualizados
        for tarifa in updated_tarifas:
            self.__carelink_session.refresh(tarifa)
        
        return updated_tarifas

    # Métodos para visitas domiciliarias
    def get_user_home_visits(self, user_id: int) -> List[VisitasDomiciliarias]:
        """Obtener todas las visitas domiciliarias de un usuario"""
        return self.__carelink_session.query(VisitasDomiciliarias).filter(
            VisitasDomiciliarias.id_usuario == user_id
        ).order_by(VisitasDomiciliarias.fecha_visita.desc()).all()

    def get_home_visit_by_id(self, visita_id: int) -> VisitasDomiciliarias:
        """Obtener una visita domiciliaria por ID"""
        visita = self.__carelink_session.query(VisitasDomiciliarias).filter(
            VisitasDomiciliarias.id_visitadomiciliaria == visita_id
        ).first()
        
        if not visita:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visita domiciliaria no encontrada"
            )
        
        return visita

    def create_home_visit_manual(self, visita_data: dict, id_profesional_asignado: int = None) -> VisitasDomiciliarias:
        """Crear una visita domiciliaria manualmente"""
        from datetime import datetime
        
        visita_data["fecha_creacion"] = datetime.utcnow()
        visita_data["fecha_actualizacion"] = datetime.utcnow()
        
        visita = VisitasDomiciliarias(**visita_data)
        self.__carelink_session.add(visita)
        self.__carelink_session.commit()
        self.__carelink_session.refresh(visita)
        
        # Si se proporciona un profesional asignado, crear la relación
        if id_profesional_asignado:
            asignacion = VisitasDomiciliariasPorProfesional(
                id_visitadomiciliaria=visita.id_visitadomiciliaria,
                id_profesional=id_profesional_asignado,
                estado_asignacion="ACTIVA",
                fecha_asignacion=datetime.utcnow()
            )
            self.__carelink_session.add(asignacion)
            self.__carelink_session.commit()
        
        return visita

    def update_home_visit(self, visita_id: int, update_data: dict) -> VisitasDomiciliarias:
        """Actualizar una visita domiciliaria"""
        from datetime import datetime
        
        visita = self.get_home_visit_by_id(visita_id)
        
        # Extraer id_profesional_asignado si existe
        id_profesional_asignado = update_data.pop("id_profesional_asignado", None)
        
        # Verificar si se está cambiando la fecha o hora de visita
        fecha_original = visita.fecha_visita
        hora_original = visita.hora_visita
        nueva_fecha = update_data.get("fecha_visita")
        nueva_hora = update_data.get("hora_visita")
        
        # Si se está cambiando la fecha o la hora, actualizar el estado a REPROGRAMADA
        # (sin importar el estado actual: PENDIENTE, REALIZADA, etc.)
        if (nueva_fecha and nueva_fecha != fecha_original) or (nueva_hora and nueva_hora != hora_original):
            update_data["estado_visita"] = "REPROGRAMADA"
        
        update_data["fecha_actualizacion"] = datetime.utcnow()
        
        for key, value in update_data.items():
            if hasattr(visita, key):
                setattr(visita, key, value)
        
        self.__carelink_session.commit()
        self.__carelink_session.refresh(visita)
        
        # Manejar la asignación del profesional
        if id_profesional_asignado is not None:
            # Primero, eliminar asignaciones existentes para esta visita
            self.__carelink_session.query(VisitasDomiciliariasPorProfesional).filter(
                VisitasDomiciliariasPorProfesional.id_visitadomiciliaria == visita_id
            ).delete()
            
            # Crear nueva asignación
            asignacion = VisitasDomiciliariasPorProfesional(
                id_visitadomiciliaria=visita_id,
                id_profesional=id_profesional_asignado,
                estado_asignacion="ACTIVA",
                fecha_asignacion=datetime.utcnow()
            )
            self.__carelink_session.add(asignacion)
            self.__carelink_session.commit()
        
        return visita

    def delete_home_visit(self, visita_id: int):
        """Eliminar una visita domiciliaria"""
        visita = self.get_home_visit_by_id(visita_id)
        
        self.__carelink_session.delete(visita)
        self.__carelink_session.commit()

    def get_home_visits_with_professionals(self, user_id: int) -> List[dict]:
        """Obtener visitas domiciliarias con información del profesional asignado"""
        from sqlalchemy.orm import joinedload
        from datetime import datetime
        from app.models.user import User
        
        # Primero, actualizar automáticamente el estado de las visitas vencidas
        self._update_expired_visits_status()
        
        visitas = self.__carelink_session.query(VisitasDomiciliarias).options(
            joinedload(VisitasDomiciliarias.usuario)
        ).filter(
            VisitasDomiciliarias.id_usuario == user_id
        ).order_by(VisitasDomiciliarias.fecha_visita.desc()).all()
        
        result = []
        for visita in visitas:
            # Intentar obtener el usuario directamente si la relación no funciona
            paciente_nombre = "Sin paciente"
            if visita.usuario:
                paciente_nombre = f"{visita.usuario.nombres} {visita.usuario.apellidos}"
            elif visita.id_usuario:
                # Buscar el usuario directamente en la base de datos
                usuario_directo = self.__carelink_session.query(User).filter(User.id_usuario == visita.id_usuario).first()
                if usuario_directo:
                    paciente_nombre = f"{usuario_directo.nombres} {usuario_directo.apellidos}"
            
            visita_dict = {
                "id_visitadomiciliaria": visita.id_visitadomiciliaria,
                "id_contrato": visita.id_contrato,
                "id_usuario": visita.id_usuario,
                "fecha_visita": visita.fecha_visita,
                "hora_visita": visita.hora_visita,
                "estado_visita": visita.estado_visita,
                "direccion_visita": visita.direccion_visita,
                "telefono_visita": visita.telefono_visita,
                "valor_dia": visita.valor_dia,
                "observaciones": visita.observaciones,
                "fecha_creacion": visita.fecha_creacion,
                "fecha_actualizacion": visita.fecha_actualizacion,
                "profesional_asignado": None,
                "paciente_nombre": paciente_nombre
            }
            
            # Buscar si hay un profesional asignado
            asignacion = self.__carelink_session.query(VisitasDomiciliariasPorProfesional).filter(
                VisitasDomiciliariasPorProfesional.id_visitadomiciliaria == visita.id_visitadomiciliaria,
                VisitasDomiciliariasPorProfesional.estado_asignacion == "ACTIVA"
            ).first()
            
            if asignacion:
                profesional = self.__carelink_session.query(Profesionales).filter(
                    Profesionales.id_profesional == asignacion.id_profesional
                ).first()
                if profesional:
                    visita_dict["profesional_asignado"] = f"{profesional.nombres} {profesional.apellidos}"
            
            result.append(visita_dict)
        
        return result

    def get_all_home_visits_with_professionals(self) -> List[dict]:
        """Obtener todas las visitas domiciliarias con información del profesional asignado"""
        from sqlalchemy.orm import joinedload
        
        # Primero, actualizar automáticamente el estado de las visitas vencidas
        self._update_expired_visits_status()
        
        visitas = self.__carelink_session.query(VisitasDomiciliarias).options(
            joinedload(VisitasDomiciliarias.usuario)
        ).order_by(VisitasDomiciliarias.fecha_visita.desc()).all()
        
        result = []
        for visita in visitas:
            # Intentar obtener el usuario directamente si la relación no funciona
            paciente_nombre = "Sin paciente"
            if visita.usuario:
                paciente_nombre = f"{visita.usuario.nombres} {visita.usuario.apellidos}"
            elif visita.id_usuario:
                # Buscar el usuario directamente en la base de datos
                usuario_directo = self.__carelink_session.query(User).filter(User.id_usuario == visita.id_usuario).first()
                if usuario_directo:
                    paciente_nombre = f"{usuario_directo.nombres} {usuario_directo.apellidos}"
            
            visita_dict = {
                "id_visitadomiciliaria": visita.id_visitadomiciliaria,
                "id_contrato": visita.id_contrato,
                "id_usuario": visita.id_usuario,
                "fecha_visita": visita.fecha_visita,
                "hora_visita": visita.hora_visita,
                "estado_visita": visita.estado_visita,
                "direccion_visita": visita.direccion_visita,
                "telefono_visita": visita.telefono_visita,
                "valor_dia": visita.valor_dia,
                "observaciones": visita.observaciones,
                "fecha_creacion": visita.fecha_creacion,
                "fecha_actualizacion": visita.fecha_actualizacion,
                "profesional_asignado": None,
                "paciente_nombre": paciente_nombre
            }
            
            # Buscar si hay un profesional asignado
            asignacion = self.__carelink_session.query(VisitasDomiciliariasPorProfesional).filter(
                VisitasDomiciliariasPorProfesional.id_visitadomiciliaria == visita.id_visitadomiciliaria,
                VisitasDomiciliariasPorProfesional.estado_asignacion == "ACTIVA"
            ).first()
            
            if asignacion:
                profesional = self.__carelink_session.query(Profesionales).filter(
                    Profesionales.id_profesional == asignacion.id_profesional
                ).first()
                if profesional:
                    visita_dict["profesional_asignado"] = f"{profesional.nombres} {profesional.apellidos} ({profesional.especialidad})"
            
            result.append(visita_dict)
        
        return result

    def _update_expired_visits_status(self):
        """Actualizar automáticamente el estado de las visitas vencidas a REALIZADA"""
        from datetime import datetime
        
        now = datetime.now()
        
        # Buscar visitas que están pendientes (las reprogramadas se manejan por separado)
        pending_visits = self.__carelink_session.query(VisitasDomiciliarias).filter(
            VisitasDomiciliarias.estado_visita == 'PENDIENTE'
        ).all()
        
        expired_visits = []
        
        for visita in pending_visits:
            # Solo procesar visitas que tengan fecha y hora programadas
            if visita.fecha_visita and visita.hora_visita:
                # Crear datetime combinando fecha y hora de la visita
                visita_datetime = datetime.combine(visita.fecha_visita, visita.hora_visita)
                
                
                # Si la fecha y hora de la visita ya pasó, marcarla como vencida
                if visita_datetime < now:  # Cambiado de <= a < para ser más preciso
                    visita.estado_visita = "REALIZADA"
                    visita.fecha_actualizacion = now
                    expired_visits.append(visita)
   
        if expired_visits:
            self.__carelink_session.commit()
        
        # Procesar visitas reprogramadas por separado
        self._update_reprogrammed_visits_status()

    def _update_reprogrammed_visits_status(self):
        """Actualizar automáticamente el estado de las visitas reprogramadas vencidas a REALIZADA"""
        from datetime import datetime
        
        now = datetime.now()
        
        # Buscar visitas reprogramadas
        reprogrammed_visits = self.__carelink_session.query(VisitasDomiciliarias).filter(
            VisitasDomiciliarias.estado_visita == 'REPROGRAMADA'
        ).all()
        
        expired_reprogrammed_visits = []
        
        for visita in reprogrammed_visits:
            # Solo procesar visitas que tengan fecha y hora programadas
            if visita.fecha_visita and visita.hora_visita:
                # Crear datetime combinando fecha y hora de la visita
                visita_datetime = datetime.combine(visita.fecha_visita, visita.hora_visita)
                
                # Si la fecha y hora de la visita reprogramada ya pasó, marcarla como vencida
                if visita_datetime < now:  # Cambiado de <= a < para ser más preciso
                    visita.estado_visita = "REALIZADA"
                    visita.fecha_actualizacion = now
                    expired_reprogrammed_visits.append(visita)
        
        if expired_reprogrammed_visits:
            self.__carelink_session.commit()

    def get_scheduled_home_visits_with_professionals(self) -> List[dict]:
        """Obtener solo las visitas domiciliarias programadas (futuras) con información del profesional asignado"""
        from sqlalchemy.orm import joinedload
        from datetime import date
        
        # Primero, actualizar automáticamente el estado de las visitas vencidas
        self._update_expired_visits_status()
        
        # Obtener solo visitas con fecha y hora futuras
        from datetime import datetime
        
        now = datetime.now()
        
        visitas = self.__carelink_session.query(VisitasDomiciliarias).options(
            joinedload(VisitasDomiciliarias.usuario)
        ).order_by(VisitasDomiciliarias.fecha_visita.asc()).all()
        
        # Filtrar visitas que realmente están en el futuro (considerando fecha y hora)
        result_visitas = []
        for visita in visitas:
            if visita.fecha_visita and visita.hora_visita:
                visita_datetime = datetime.combine(visita.fecha_visita, visita.hora_visita)
                if visita_datetime > now:
                    result_visitas.append(visita)
            else:
                # Si no tiene fecha/hora programada, incluirla (pendiente de programación)
                result_visitas.append(visita)
        
        result = []
        for visita in result_visitas:
            visita_dict = {
                "id_visitadomiciliaria": visita.id_visitadomiciliaria,
                "id_contrato": visita.id_contrato,
                "id_usuario": visita.id_usuario,
                "fecha_visita": visita.fecha_visita,
                "hora_visita": visita.hora_visita,
                "estado_visita": visita.estado_visita,
                "direccion_visita": visita.direccion_visita,
                "telefono_visita": visita.telefono_visita,
                "valor_dia": visita.valor_dia,
                "observaciones": visita.observaciones,
                "fecha_creacion": visita.fecha_creacion,
                "fecha_actualizacion": visita.fecha_actualizacion,
                "profesional_asignado": None,
                "paciente_nombre": f"{visita.usuario.nombres} {visita.usuario.apellidos}" if visita.usuario else "Sin paciente"
            }
            
            # Buscar si hay un profesional asignado
            asignacion = self.__carelink_session.query(VisitasDomiciliariasPorProfesional).filter(
                VisitasDomiciliariasPorProfesional.id_visitadomiciliaria == visita.id_visitadomiciliaria,
                VisitasDomiciliariasPorProfesional.estado_asignacion == "ACTIVA"
            ).first()
            
            if asignacion:
                profesional = self.__carelink_session.query(Profesionales).filter(
                    Profesionales.id_profesional == asignacion.id_profesional
                ).first()
                if profesional:
                    visita_dict["profesional_asignado"] = f"{profesional.nombres} {profesional.apellidos} ({profesional.especialidad})"
            
            result.append(visita_dict)
        
        return result

    def get_user_flow_data(self):
        """
        Obtiene los datos del flujo de usuarios para el dashboard.
        Incluye estadísticas y lista de usuarios con visitas domiciliarias = false.
        """
        from app.dto.v1.response.user_flow import UserFlowResponseDTO, UserFlowStatsDTO, UserFlowItemDTO
        from datetime import datetime, date
        from sqlalchemy import and_, extract, func
        from app.models.user import User
        from app.models.contracts import Contratos
        from app.models.attendance_schedule import CronogramaAsistencia, CronogramaAsistenciaPacientes, EstadoAsistencia
        
        try:
            # Obtener usuarios con visitas domiciliarias = false
            users_query = self.__carelink_session.query(User).filter(
                and_(
                    User.visitas_domiciliarias == False,
                    User.is_deleted == False
                )
            ).all()
            
            # Obtener contratos activos para estos usuarios
            user_contracts = {}
            for user in users_query:
                contract = self.__carelink_session.query(Contratos).filter(
                    and_(
                        Contratos.id_usuario == user.id_usuario,
                        Contratos.estado == "ACTIVO"
                    )
                ).first()
                if contract:
                    user_contracts[user.id_usuario] = contract.id_contrato
            
            # Obtener visitas del mes actual para cada usuario
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            user_visits = {}
            for user in users_query:
                if user.id_usuario in user_contracts:
                    contract_id = user_contracts[user.id_usuario]
                    
                    # Contar visitas programadas para el mes actual
                    visits_count = self.__carelink_session.query(CronogramaAsistenciaPacientes).join(
                        CronogramaAsistencia
                    ).filter(
                        and_(
                            CronogramaAsistenciaPacientes.id_contrato == contract_id,
                            CronogramaAsistenciaPacientes.id_usuario == user.id_usuario,
                            extract('month', CronogramaAsistencia.fecha) == current_month,
                            extract('year', CronogramaAsistencia.fecha) == current_year
                        )
                    ).count()
                    
                    user_visits[user.id_usuario] = visits_count
            
            # Crear lista de usuarios con sus datos
            users_list = []
            for user in users_query:
                if user.id_usuario in user_contracts:
                    users_list.append(UserFlowItemDTO(
                        id_usuario=user.id_usuario,
                        nombre_completo=f"{user.nombres} {user.apellidos}",
                        id_contrato=user_contracts[user.id_usuario],
                        visitas_mes=user_visits.get(user.id_usuario, 0)
                    ))
            
            # Calcular estadísticas
            total_users_month = len(users_list)
            
            # Calcular tasa de asistencia (simplificado - se puede mejorar)
            total_visits_scheduled = sum(user_visits.values())
            total_visits_attended = self.__carelink_session.query(CronogramaAsistenciaPacientes).join(
                CronogramaAsistencia
            ).filter(
                and_(
                    CronogramaAsistenciaPacientes.estado_asistencia == EstadoAsistencia.ASISTIO,
                    extract('month', CronogramaAsistencia.fecha) == current_month,
                    extract('year', CronogramaAsistencia.fecha) == current_year
                )
            ).count()
            
            tasa_asistencia = (total_visits_attended / total_visits_scheduled * 100) if total_visits_scheduled > 0 else 0
            
            # Calcular tendencias (simplificado - se puede mejorar)
            # Para este ejemplo, usamos valores fijos, pero se pueden calcular comparando con meses anteriores
            usuarios_mes_trend = 17.1  # Porcentaje de crecimiento
            tasa_asistencia_trend = 26.2  # Porcentaje de crecimiento
            
            stats = UserFlowStatsDTO(
                usuarios_mes=total_users_month,
                tasa_asistencia=round(tasa_asistencia, 1),
                usuarios_mes_trend=usuarios_mes_trend,
                tasa_asistencia_trend=tasa_asistencia_trend
            )
            
            return UserFlowResponseDTO(
                stats=stats,
                users=users_list
            )
            
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener datos del flujo de usuarios: {str(e)}"
            )

    def get_quarterly_visits_data(self):
        """
        Obtiene los datos de visitas del trimestre para el dashboard.
        Incluye estadísticas trimestrales y datos mensuales para el gráfico.
        """
        from app.dto.v1.response.quarterly_visits import QuarterlyVisitsResponseDTO, MonthlyVisitData
        from datetime import datetime, date, timedelta
        from sqlalchemy import and_, extract, func
        from app.models.home_visit import VisitasDomiciliarias
        
        try:
            # Obtener datos de la tabla
            total_visits = self.__carelink_session.query(VisitasDomiciliarias).count()
            
            # Calcular el trimestre actual
            now = datetime.now()
            current_month = now.month
            current_year = now.year
            
            # Determinar el trimestre actual (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
            if current_month <= 3:
                quarter_start_month = 1
                quarter_end_month = 3
                quarter_name = "Q1"
            elif current_month <= 6:
                quarter_start_month = 4
                quarter_end_month = 6
                quarter_name = "Q2"
            elif current_month <= 9:
                quarter_start_month = 7
                quarter_end_month = 9
                quarter_name = "Q3"
            else:
                quarter_start_month = 10
                quarter_end_month = 12
                quarter_name = "Q4"
            
            # Obtener visitas del trimestre actual
            quarterly_visits = self.__carelink_session.query(VisitasDomiciliarias).filter(
                and_(
                    extract('year', VisitasDomiciliarias.fecha_visita) == current_year,
                    extract('month', VisitasDomiciliarias.fecha_visita) >= quarter_start_month,
                    extract('month', VisitasDomiciliarias.fecha_visita) <= quarter_end_month,
                    VisitasDomiciliarias.fecha_visita.isnot(None)
                )
            ).all()
            
            total_quarterly_visits = len(quarterly_visits)
            
            # Calcular promedio de visitas por día del trimestre
            if total_quarterly_visits > 0:
                # Contar días del trimestre
                quarter_start = date(current_year, quarter_start_month, 1)
                if quarter_end_month == 12:
                    quarter_end = date(current_year + 1, 1, 1) - timedelta(days=1)
                else:
                    quarter_end = date(current_year, quarter_end_month + 1, 1) - timedelta(days=1)
                
                days_in_quarter = (quarter_end - quarter_start).days + 1
                average_daily_visits = round(total_quarterly_visits / days_in_quarter, 1)
            else:
                average_daily_visits = 0.0
            
            # Obtener datos mensuales para el gráfico (últimos 6 meses)
            monthly_data = []
            month_names = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            
            for i in range(6):
                # Calcular mes y año
                target_month = current_month - i
                target_year = current_year
                
                if target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                # Contar visitas del mes
                month_visits = self.__carelink_session.query(VisitasDomiciliarias).filter(
                    and_(
                        extract('year', VisitasDomiciliarias.fecha_visita) == target_year,
                        extract('month', VisitasDomiciliarias.fecha_visita) == target_month
                    )
                ).count()
                
                monthly_data.append(MonthlyVisitData(
                    month=month_names[target_month - 1],
                    visits=month_visits
                ))

            
            # Invertir la lista para mostrar en orden cronológico
            monthly_data.reverse()
            
            # Obtener visitas del mes actual y anterior para calcular crecimiento
            current_month_visits = self.__carelink_session.query(VisitasDomiciliarias).filter(
                and_(
                    extract('year', VisitasDomiciliarias.fecha_visita) == current_year,
                    extract('month', VisitasDomiciliarias.fecha_visita) == current_month,
                    VisitasDomiciliarias.fecha_visita.isnot(None)
                )
            ).count()
            
            # Calcular mes anterior
            previous_month = current_month - 1
            previous_year = current_year
            if previous_month <= 0:
                previous_month = 12
                previous_year -= 1
            
            previous_month_visits = self.__carelink_session.query(VisitasDomiciliarias).filter(
                and_(
                    extract('year', VisitasDomiciliarias.fecha_visita) == previous_year,
                    extract('month', VisitasDomiciliarias.fecha_visita) == previous_month,
                    VisitasDomiciliarias.fecha_visita.isnot(None)
                )
            ).count()
            
            # Calcular porcentaje de crecimiento
            if previous_month_visits > 0:
                growth_percentage = round(((current_month_visits - previous_month_visits) / previous_month_visits) * 100, 1)
            else:
                growth_percentage = 0.0 if current_month_visits == 0 else 100.0
            
            return QuarterlyVisitsResponseDTO(
                total_quarterly_visits=total_quarterly_visits,
                average_daily_visits=average_daily_visits,
                monthly_data=monthly_data,
                current_month_visits=current_month_visits,
                previous_month_visits=previous_month_visits,
                growth_percentage=growth_percentage
            )
            
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener datos de visitas trimestrales: {str(e)}"
            )

    def get_monthly_payments_data(self):
        """
        Obtiene los datos de pagos mensuales para el dashboard.
        Incluye estadísticas de pagos y metas basadas en el mes anterior.
        """
        from app.dto.v1.response.monthly_payments import MonthlyPaymentsResponseDTO, MonthlyPaymentData
        from datetime import datetime, date, timedelta
        from sqlalchemy import and_, extract, func
        from app.models.contracts import Pagos, Facturas
        
        try:
            # Calcular el mes actual
            now = datetime.now()
            current_month = now.month
            current_year = now.year
            
            # Obtener datos mensuales para el gráfico (últimos 6 meses)
            monthly_data = []
            month_names = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            
            previous_month_payments = 0
            current_month_payments = 0
            total_payments = 0
            
            for i in range(6):
                # Calcular mes y año
                target_month = current_month - i
                target_year = current_year
                
                if target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                # Obtener pagos del mes (suma de todos los pagos del mes)
                month_payments = self.__carelink_session.query(func.sum(Pagos.valor)).filter(
                    and_(
                        extract('year', Pagos.fecha_pago) == target_year,
                        extract('month', Pagos.fecha_pago) == target_month,
                        Pagos.valor.isnot(None)
                    )
                ).scalar() or 0.0
                
                # Convertir a float si es Decimal
                month_payments = float(month_payments)
                
                # Calcular meta del mes (el valor del mes anterior si es superior, sino mantener el actual)
                if i == 0:  # Mes actual
                    goal = previous_month_payments if previous_month_payments > month_payments else month_payments
                    current_month_payments = month_payments
                else:
                    # Para meses anteriores, la meta es el valor del mes anterior
                    goal = previous_month_payments if previous_month_payments > 0 else month_payments
                
                # Calcular porcentaje de cumplimiento
                achievement_percentage = (month_payments / goal * 100) if goal > 0 else 0
                
                monthly_data.append(MonthlyPaymentData(
                    month=month_names[target_month - 1],
                    payments=month_payments,
                    goal=goal,
                    achievement_percentage=round(achievement_percentage, 1)
                ))
                
                # Actualizar para el siguiente mes
                previous_month_payments = month_payments
                total_payments += month_payments
            
            # Invertir la lista para mostrar en orden cronológico
            monthly_data.reverse()
            
            # Calcular porcentaje de cumplimiento general (promedio de los últimos 6 meses)
            overall_goal_achievement = sum(item.achievement_percentage for item in monthly_data) / len(monthly_data) if monthly_data else 0
            
            return MonthlyPaymentsResponseDTO(
                total_payments=total_payments,
                current_month_payments=current_month_payments,
                previous_month_payments=previous_month_payments,
                monthly_data=monthly_data,
                overall_goal_achievement=round(overall_goal_achievement, 1)
            )
            
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener datos de pagos mensuales: {str(e)}"
            )

    def get_operational_efficiency_data(self):
        """
        Obtiene los datos de eficiencia operativa para el dashboard.
        Combina múltiples métricas: asistencia, visitas domiciliarias, contratos y facturación.
        """
        from app.dto.v1.response.operational_efficiency import OperationalEfficiencyResponseDTO, MonthlyEfficiencyData
        from datetime import datetime, date, timedelta
        from sqlalchemy import and_, extract, func
        from app.models.contracts import Contratos, Facturas, Pagos
        from app.models.attendance_schedule import CronogramaAsistencia, CronogramaAsistenciaPacientes, EstadoAsistencia
        from app.models.home_visit import VisitasDomiciliarias
        
        try:
            # Calcular el mes actual
            now = datetime.now()
            current_month = now.month
            current_year = now.year
            
            # Obtener datos mensuales para el gráfico (últimos 6 meses)
            monthly_data = []
            month_names = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            
            previous_month_efficiency = 0
            current_month_efficiency = 0
            
            for i in range(6):
                # Calcular mes y año
                target_month = current_month - i
                target_year = current_year
                
                if target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                # 1. Calcular tasa de asistencia del mes
                total_scheduled = self.__carelink_session.query(CronogramaAsistenciaPacientes).join(
                    CronogramaAsistencia
                ).filter(
                    and_(
                        extract('year', CronogramaAsistencia.fecha) == target_year,
                        extract('month', CronogramaAsistencia.fecha) == target_month
                    )
                ).count()
                
                total_attended = self.__carelink_session.query(CronogramaAsistenciaPacientes).join(
                    CronogramaAsistencia
                ).filter(
                    and_(
                        CronogramaAsistenciaPacientes.estado_asistencia == EstadoAsistencia.ASISTIO,
                        extract('year', CronogramaAsistencia.fecha) == target_year,
                        extract('month', CronogramaAsistencia.fecha) == target_month
                    )
                ).count()
                
                attendance_rate = (total_attended / total_scheduled * 100) if total_scheduled > 0 else 0
                
                # 2. Calcular cumplimiento de visitas domiciliarias
                total_home_visits = self.__carelink_session.query(VisitasDomiciliarias).filter(
                    and_(
                        extract('year', VisitasDomiciliarias.fecha_visita) == target_year,
                        extract('month', VisitasDomiciliarias.fecha_visita) == target_month
                    )
                ).count()
                
                completed_home_visits = self.__carelink_session.query(VisitasDomiciliarias).filter(
                    and_(
                        VisitasDomiciliarias.estado_visita == "REALIZADA",
                        extract('year', VisitasDomiciliarias.fecha_visita) == target_year,
                        extract('month', VisitasDomiciliarias.fecha_visita) == target_month
                    )
                ).count()
                
                home_visits_completion = (completed_home_visits / total_home_visits * 100) if total_home_visits > 0 else 0
                
                # 3. Calcular eficiencia en gestión de contratos
                total_contracts = self.__carelink_session.query(Contratos).filter(
                    and_(
                        extract('year', Contratos.fecha_inicio) == target_year,
                        extract('month', Contratos.fecha_inicio) == target_month
                    )
                ).count()
                
                active_contracts = self.__carelink_session.query(Contratos).filter(
                    and_(
                        Contratos.estado == "ACTIVO",
                        extract('year', Contratos.fecha_inicio) == target_year,
                        extract('month', Contratos.fecha_inicio) == target_month
                    )
                ).count()
                
                contract_management = (active_contracts / total_contracts * 100) if total_contracts > 0 else 0
                
                # 4. Calcular eficiencia en facturación
                total_bills = self.__carelink_session.query(Facturas).filter(
                    and_(
                        extract('year', Facturas.fecha_emision) == target_year,
                        extract('month', Facturas.fecha_emision) == target_month
                    )
                ).count()
                
                paid_bills = self.__carelink_session.query(Facturas).filter(
                    and_(
                        Facturas.estado_factura == "PAGADA",
                        extract('year', Facturas.fecha_emision) == target_year,
                        extract('month', Facturas.fecha_emision) == target_month
                    )
                ).count()
                
                billing_efficiency = (paid_bills / total_bills * 100) if total_bills > 0 else 0
                
                # 5. Calcular eficiencia general (promedio ponderado)
                efficiency = (
                    attendance_rate * 0.3 +  # 30% peso para asistencia
                    home_visits_completion * 0.25 +  # 25% peso para visitas domiciliarias
                    contract_management * 0.25 +  # 25% peso para contratos
                    billing_efficiency * 0.2  # 20% peso para facturación
                )
                
                monthly_data.append(MonthlyEfficiencyData(
                    month=month_names[target_month - 1],
                    efficiency=round(efficiency, 1),
                    attendance_rate=round(attendance_rate, 1),
                    home_visits_completion=round(home_visits_completion, 1),
                    contract_management=round(contract_management, 1),
                    billing_efficiency=round(billing_efficiency, 1)
                ))
                
                # Actualizar para el siguiente mes
                if i == 0:  # Mes actual
                    current_month_efficiency = efficiency
                elif i == 1:  # Mes anterior
                    previous_month_efficiency = efficiency
            
            # Invertir la lista para mostrar en orden cronológico
            monthly_data.reverse()
            
            # Calcular eficiencia general (promedio de los últimos 6 meses)
            overall_efficiency = sum(item.efficiency for item in monthly_data) / len(monthly_data) if monthly_data else 0
            
            # Calcular porcentaje de crecimiento
            growth_percentage = ((current_month_efficiency - previous_month_efficiency) / previous_month_efficiency * 100) if previous_month_efficiency > 0 else 0
            
            # Calcular métricas actuales para el mes actual
            current_attendance_rate = monthly_data[-1].attendance_rate if monthly_data else 0
            current_home_visits_completion = monthly_data[-1].home_visits_completion if monthly_data else 0
            current_contract_management = monthly_data[-1].contract_management if monthly_data else 0
            current_billing_efficiency = monthly_data[-1].billing_efficiency if monthly_data else 0
            
            return OperationalEfficiencyResponseDTO(
                overall_efficiency=round(overall_efficiency, 1),
                current_month_efficiency=round(current_month_efficiency, 1),
                previous_month_efficiency=round(previous_month_efficiency, 1),
                monthly_data=monthly_data,
                attendance_rate=round(current_attendance_rate, 1),
                home_visits_completion_rate=round(current_home_visits_completion, 1),
                contract_management_rate=round(current_contract_management, 1),
                billing_efficiency_rate=round(current_billing_efficiency, 1),
                growth_percentage=round(growth_percentage, 1)
            )
            
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener datos de eficiencia operativa: {str(e)}"
            )


def get_bill_payments_total(db, id_factura: int) -> float:
    """
    Retorna el total de pagos asociados a una factura
    """
    from app.models.contracts import Pagos
    pagos = db.query(Pagos).filter(Pagos.id_factura == id_factura).all()
    total = sum(float(pago.valor) for pago in pagos)
    return total



