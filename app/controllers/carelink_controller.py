from botocore.compat import HTTPResponse
from sqlalchemy import func
from app.crud.carelink_crud import CareLinkCrud
from app.database.connection import get_carelink_db
from app.dto.v1.request.activities import (
    ActividadesGrupalesCreate,
    ActividadesGrupalesUpdate,
)
from app.dto.v1.request.bill import CalculatePartialBillRequestDTO
from app.dto.v1.request.clinical_evolution import (
    ClinicalEvolutionCreate,
    ClinicalEvolutionUpdate,
)
from app.dto.v1.request.family_member_create_request_dto import (
    AssociateFamilyMemberRequestDTO,
    CreateFamilyMemberRequestDTO,
    UpdateFamilyMemberRequestDTO,
)
from app.dto.v1.request.medical_report import ReporteClinicoCreate, ReporteClinicoUpdate
from app.dto.v1.request.payment_method import CreateUserPaymentRequestDTO
from app.dto.v1.request.user_create_request_dto import AuthorizedUserCreateRequestDTO
from app.dto.v1.request.user_medical_record_create_request_dto import (
    CreateUserAssociatedCaresRequestDTO,
    CreateUserAssociatedInterventionsRequestDTO,
    CreateUserAssociatedMedicinesRequestDTO,
    CreateUserAssociatedVaccinesRequestDTO,
    CreateUserMedicalRecordCreateRequestDTO,
)
from app.dto.v1.request.user_medical_record_update_request_dto import (
    UpdateUserMedicalRecordRequestDTO,
)
from app.dto.v1.request.user_request_dto import UserCreateRequestDTO
from app.dto.v1.response.activities import ActivitiesResponse, TypeOfActivityResponse
from app.dto.v1.response.cares_per_user import (
    CaresPerUserResponseDTO,
    CaresPerUserUpdateDTO,
)
from app.dto.v1.response.clinical_evolution import ClinicalEvolutionResponse
from app.dto.v1.response.create_user import CreateUserResponseDTO
from app.dto.v1.request.user_login_request_dto import UserLoginRequestDTO
from app.dto.v1.response.create_user_medical_record import (
    CreateUserMedicalRecordResponseDTO,
)
from app.dto.v1.response.family_member import FamilyMemberResponseDTO
from app.dto.v1.response.generic_response import Response
from app.dto.v1.response.interventions_per_user import (
    InterventionsPerUserResponseDTO,
    InterventionsPerUserUpdateDTO,
)
from app.dto.v1.response.medical_report import ReporteClinicoResponse
from app.dto.v1.response.medicines_per_user import (
    MedicinesPerUserResponseDTO,
    MedicinesPerUserUpdateDTO,
)
from app.dto.v1.response.payment_method import (
    PaymentMethodResponseDTO,
    PaymentResponseDTO,
)
from app.dto.v1.response.professional import ProfessionalResponse
from app.dto.v1.response.user_info import UserInfo
from app.dto.v1.response.user import UserResponseDTO
from app.dto.v1.response.family_members_by_user import FamilyMembersByUserResponseDTO
from app.dto.v1.response.vaccines_per_user import (
    VaccinesPerUserResponseDTO,
    VaccinesPerUserUpdateDTO,
)
from app.models.activities import ActividadesGrupales
from app.models.authorized_users import AuthorizedUsers
from app.models.cares_per_user import CuidadosEnfermeriaPorUsuario
from app.models.clinical_evolutions import EvolucionesClinicas
from app.models.family_member import FamilyMember
from app.models.interventions_per_user import IntervencionesPorUsuario
from app.models.medical_record import MedicalRecord
from app.models.medical_report import ReportesClinicos
from app.models.medicines_per_user import MedicamentosPorUsuario
from app.models.user import User
from app.models.contracts import (
    Contratos,
    Facturas,
    MetodoPago,
    Pagos,
    ServiciosPorContrato,
    FechasServicio,
    TipoPago,
)
from app.dto.v1.request.contracts import (
    ContratoCreateDTO,
    ContratoUpdateDTO,
    FacturaCreate,
    PagoCreate,
    PagoCreateDTO,
    PagoResponseDTO,
)
from app.dto.v1.request.attendance_schedule import (
    CronogramaAsistenciaCreateDTO,
    CronogramaAsistenciaPacienteCreateDTO,
    CronogramaAsistenciaUpdateDTO,
    EstadoAsistenciaUpdateDTO,
)
from app.dto.v1.response.contracts import (
    ContratoResponseDTO,
    FacturaOut,
    FechaServicioDTO,
    ServicioContratoDTO,
)
from app.dto.v1.response.attendance_schedule import (
    CronogramaAsistenciaResponseDTO,
    CronogramaAsistenciaPacienteResponseDTO,
    PacientePorFechaDTO,
)
# Nuevos imports para transporte
from app.models.transporte import CronogramaTransporte
from app.dto.v1.request.transport_schedule import (
    CronogramaTransporteCreateDTO,
    CronogramaTransporteUpdateDTO,
    RutaTransporteCreateDTO,
)
from app.dto.v1.response.transport_schedule import (
    CronogramaTransporteResponseDTO,
    RutaTransporteResponseDTO,
    RutaDiariaResponseDTO,
)
from app.models.vaccines import VacunasPorUsuario
from app.security.jwt_utilities import (
    decode_access_token,
    create_access_token,
    hash_password,
)
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import lru_cache
from http import HTTPStatus
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time
import json
from app.models.attendance_schedule import CronogramaAsistencia, CronogramaAsistenciaPacientes


token_auth_scheme = HTTPBearer()
router = APIRouter()


@lru_cache()
def get_crud(
    carelink_db: Session = Depends(get_carelink_db),
):
    return CareLinkCrud(carelink_db)


def get_payload(token: str = Depends(token_auth_scheme)):
    payload = decode_access_token(token.credentials)
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
    crud: CareLinkCrud = Depends(get_crud),
) -> AuthorizedUsers:
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas. Revise sus datos e intente de nuevo.",
        )

    user = crud._get_authorized_user_info(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users", response_model=Response[List[UserResponseDTO]])
async def list_users(
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[List[UserResponseDTO]]:
    users = crud.list_users()
    users_list = []
    for user in users:
        users_list.append(user.__dict__)
    return Response[List[UserResponseDTO]](
        data=users_list,
        status_code=HTTPStatus.OK,
        message="Usuarios consultados con éxito",
        error=None,
    )


@router.get("/users/{id}", response_model=Response[UserResponseDTO])
async def list_user_by_id(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[UserResponseDTO]:
    user = crud.list_user_by_user_id(id)
    user_response = UserResponseDTO(**user.__dict__)
    return Response[UserResponseDTO](
        data=user_response,
        status_code=HTTPStatus.OK,
        message="Usuario consultado con éxito",
        error=None,
    )


@router.get(
    "/family_members",
    status_code=200,
    response_model=Response[List[FamilyMemberResponseDTO]],
)
async def get_family_members(
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    family_members = crud._get_family_members()
    family_members_dto = [
        FamilyMemberResponseDTO.from_orm(member) for member in family_members
    ]
    return Response[List[FamilyMemberResponseDTO]](
        data=family_members_dto,
        message="Acudientes consultados exitosamente",
        error=None,
        status_code=HTTPStatus.OK,
    )


@router.get(
    "/family_members/{id}",
    status_code=200,
    response_model=Response[FamilyMemberResponseDTO],
)
async def get_family_member_by_id(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    family_member, parentesco = crud._get_family_member_by_id(id)
    family_member.parentesco = parentesco
    family_member_dto = FamilyMemberResponseDTO.from_orm(family_member)

    return Response[FamilyMemberResponseDTO](
        data=family_member_dto,
        message="Acudiente consultado exitosamente",
        error=None,
        status_code=HTTPStatus.OK,
    )


@router.get(
    "/users/{id}/family_members",
    status_code=200,
    response_model=Response[List[FamilyMembersByUserResponseDTO]],
)
async def get_user_family_members(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    family_members = crud._get_family_members_by_user_id(id)
    family_members_dto = [
        FamilyMembersByUserResponseDTO.from_orm(member) for member in family_members
    ]
    return Response[List[FamilyMembersByUserResponseDTO]](
        data=family_members_dto,
        message="Acudientes consultados de manera exitosa",
        error=None,
        status_code=HTTPStatus.OK,
    )


@router.get(
    "/users/{id}/medical_record",
    status_code=200,
    response_model=Response[CreateUserMedicalRecordResponseDTO | None],
)
async def get_user_medical_record(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    medical_record = crud.list_user_medical_record(id)
    medical_record_response = None
    if medical_record:
        medical_record_response = CreateUserMedicalRecordResponseDTO(
            **medical_record.__dict__
        )

    return Response[CreateUserMedicalRecordResponseDTO | None](
        data=medical_record_response,
        message="Historia clínica listada",
        error=None,
        status_code=200,
    )


@router.get(
    "/record/{id}/medicines",
    status_code=200,
    response_model=Response[List[MedicinesPerUserResponseDTO]],
)
async def get_record_medicines(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    medicines = crud._get_user_medicines_by_medical_record_id(id)
    result = [
        MedicinesPerUserResponseDTO(**medicine.__dict__) for medicine in medicines
    ]
    return Response[List[MedicinesPerUserResponseDTO]](
        data=result,
        message="Medicamentos consultados con éxito",
        status_code=201,
        error=None,
    )


@router.get(
    "/record/{id}/interventions",
    status_code=200,
    response_model=Response[List[InterventionsPerUserResponseDTO]],
)
async def get_record_interventions(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    interventions = crud._get_user_interventions_by_medical_record_id(id)
    result = [
        InterventionsPerUserResponseDTO(**intervention.__dict__)
        for intervention in interventions
    ]
    return Response[List[InterventionsPerUserResponseDTO]](
        data=result, message="Success", status_code=201, error=None
    )


@router.get(
    "/record/{id}/cares",
    status_code=200,
    response_model=Response[List[CaresPerUserResponseDTO]],
)
async def get_record_cares(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    cares = crud._get_user_cares_by_medical_record_id(id)
    result = [CaresPerUserResponseDTO(**care.__dict__) for care in cares]
    return Response[List[CaresPerUserResponseDTO]](
        data=result, message="Success", status_code=201, error=None
    )


@router.get(
    "/record/{id}/vaccines",
    status_code=200,
    response_model=Response[List[VaccinesPerUserResponseDTO]],
)
async def get_record_vaccines(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    vaccines = crud._get_user_vaccines_by_medical_record_id(id)
    result = [VaccinesPerUserResponseDTO(**vaccine.__dict__) for vaccine in vaccines]
    return Response[List[VaccinesPerUserResponseDTO]](
        data=result, message="Success", status_code=201, error=None
    )


@router.get("/info", status_code=200, response_model=Response[UserInfo])
async def get_user_info(
    crud: CareLinkCrud = Depends(get_crud), payload: dict = Depends(get_payload)
):
    user = crud._get_authorized_user_info(payload["sub"])
    result = UserInfo(**user.__dict__)
    return Response[UserInfo](
        data=result,
        message="User info retrieved successfuly",
        error=None,
        status_code=HTTPStatus.OK,
    )


@router.get(
    "/medical_reports/{reporte_id}", response_model=Response[ReporteClinicoResponse]
)
def get_reporte_clinico(
    reporte_id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[ReporteClinicoResponse]:
    report = crud._get_medical_report_by_id(reporte_id)
    report_dict = report.__dict__
    professional_response = None
    if report.profesional:
        professional_response = ProfessionalResponse.from_orm(report.profesional)
    report_response = ReporteClinicoResponse(**report_dict)
    del report_response.profesional
    report_response.profesional = professional_response
    return Response[ReporteClinicoResponse](
        data=report_response,
        message="Reporte consultado",
        status_code=200,
        error=None,
    )


@router.get(
    "/user/{user_id}/medical_reports",
    response_model=Response[List[ReporteClinicoResponse]],
)
def get_medical_reports(
    user_id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[List[ReporteClinicoResponse]]:
    reports = crud._get_medical_reports_by_user_id(user_id)
    return Response[List[ReporteClinicoResponse]](
        data=[ReporteClinicoResponse(**report.__dict__) for report in reports],
        message="Reporte consultado",
        status_code=200,
        error=None,
    )


@router.get("/professionals", response_model=Response[List[ProfessionalResponse]])
async def get_professionals(
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[List[ProfessionalResponse]]:
    professionals = crud._get_professionals()
    response = [
        ProfessionalResponse.from_orm(professional) for professional in professionals
    ]
    return Response[List[ProfessionalResponse]](
        data=response, message="Lista de profesionales", status_code=200, error=None
    )


@router.get(
    "/reports/{id}/evolutions", response_model=Response[List[ClinicalEvolutionResponse]]
)
async def get_clinical_evolutions(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[List[ClinicalEvolutionResponse]]:
    evolutions = crud._get_clinical_evolutions_by_report_id(id)
    response = [
        ClinicalEvolutionResponse.from_orm(evolution) for evolution in evolutions
    ]
    return Response[List[ClinicalEvolutionResponse]](
        data=response,
        message="Evoluciones clínicas consultadas con éxito",
        error=None,
        status_code=200,
    )


@router.get("/evolutions/{id}", response_model=Response[ClinicalEvolutionResponse])
async def get_clinical_evolution(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[ClinicalEvolutionResponse]:
    evolution = crud._get_clinical_evolution_by_evolution_id(id)
    response = ClinicalEvolutionResponse.from_orm(evolution)

    return Response[ClinicalEvolutionResponse](
        data=response,
        message="Evoluciones clínicas consultadas con éxito",
        error=None,
        status_code=200,
    )


@router.get(
    "/activities",
    status_code=200,
    response_model=Response[List[ActivitiesResponse]],
)
async def get_activities(
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[List[ActivitiesResponse]]:
    activities = crud._get_activities()
    result = [ActivitiesResponse(**activity.__dict__) for activity in activities]
    return Response[List[ActivitiesResponse]](
        data=result,
        message="Actividades consultadas con éxito",
        status_code=201,
        error=None,
    )


@router.get(
    "/activities/{id}",
    status_code=200,
    response_model=Response[ActivitiesResponse],
)
async def get_activity_by_id(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[ActivitiesResponse]:
    activity = crud._get_activity_by_id(id)
    result = ActivitiesResponse(**activity.__dict__)
    return Response[ActivitiesResponse](
        data=result,
        message="Actividad consultada con éxito",
        status_code=201,
        error=None,
    )


@router.get(
    "/activity_types",
    status_code=200,
    response_model=Response[List[TypeOfActivityResponse]],
)
async def get_activity_types(
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[List[TypeOfActivityResponse]]:
    activity_types = crud._get_activity_types()
    result = [TypeOfActivityResponse(**type.__dict__) for type in activity_types]
    return Response[List[TypeOfActivityResponse]](
        data=result,
        message="Tipos de actividad consultados con éxito",
        status_code=201,
        error=None,
    )


@router.get("/metodos_pago", response_model=Response[List[PaymentMethodResponseDTO]])
async def get_payment_methods(
    crud: CareLinkCrud = Depends(get_crud),
) -> Response[List[PaymentMethodResponseDTO]]:
    payment_methods = crud._get_payment_methods()
    payment_methods_response = [
        PaymentMethodResponseDTO.from_orm(method) for method in payment_methods
    ]
    return Response[List[PaymentMethodResponseDTO]](
        data=payment_methods_response,
        status_code=HTTPStatus.OK,
        error=None,
        message="Métodos de pago retornados con éxito",
    )


@router.get(
    "/activities-upcoming",
    status_code=200,
    response_model=Response[List[ActivitiesResponse]],
)
async def get_upcoming_activities(
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[List[ActivitiesResponse]]:
    activities = crud._get_upcoming_activities()
    result = [ActivitiesResponse(**activity.__dict__) for activity in activities]
    return Response[List[ActivitiesResponse]](
        data=result,
        message="Actividades consultadas con éxito",
        status_code=201,
        error=None,
    )


@router.post("/pagos/registrar", response_model=Response[PaymentResponseDTO])
async def register_payment(
    payment: CreateUserPaymentRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[PaymentResponseDTO]:
    payment_data = Pagos(
        id_factura=payment.id_factura,
        id_metodo_pago=payment.id_metodo_pago,
        id_tipo_pago=1,
        fecha_pago=payment.fecha_pago,
        valor=payment.valor,
    )
    payment_response = crud.create_payment(payment_data)

    return Response[PaymentResponseDTO](
        data=PaymentResponseDTO.from_orm(payment_response),
        error=None,
        message="Pago creado de manera exitosa",
        status_code=HTTPStatus.CREATED,
    )


@router.post("/calcular/factura", response_model=Response[float])
async def calculate_partial_bill(
    partial_bill: CalculatePartialBillRequestDTO, crud: CareLinkCrud = Depends(get_crud)
) -> Response[float]:
    result = crud.calculate_partial_bill(
        service_ids=partial_bill.service_ids,
        quantities=partial_bill.quantities,
        year=partial_bill.year,
    )
    return Response[float](
        data=result,
        message="Factura calculada con éxito",
        status_code=HTTPStatus.OK,
        error=None,
    )


@router.post("/users", status_code=201, response_model=Response[UserResponseDTO])
async def create_users(
    user: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[UserResponseDTO]:
    try:
        user_data = UserCreateRequestDTO.parse_raw(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user data: {str(e)}")

    user_to_save = User(**user_data.dict())

    saved_user = crud.save_user(user_to_save, photo)
    user_response = UserResponseDTO(**saved_user.__dict__)

    return Response[UserResponseDTO](
        data=user_response,
        status_code=HTTPStatus.CREATED,
        message="Usuario creado de manera exitosa",
        error=None,
    )


@router.post(
    "/family_members/:id",
    status_code=201,
    response_model=Response[object],
)
async def create_family_members(
    id: int,
    family_member: CreateFamilyMemberRequestDTO,
    kinship: AssociateFamilyMemberRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    family_member_to_save = FamilyMember(**family_member.dict())
    crud.save_family_member(id, kinship, family_member_to_save)

    return Response[object](
        data={},
        status_code=HTTPStatus.CREATED,
        message="Acudiente registrado de manera exitosa",
        error=None,
    )


@router.post("/login", response_model=Response[dict])
async def login_user(
    login_data: UserLoginRequestDTO, crud: CareLinkCrud = Depends(get_crud)
) -> Response[dict]:
    user = crud.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos. Revise sus datos e intente de nuevo.",
        )

    access_token = create_access_token(data={"sub": user.id})
    return Response[dict](
        data={"access_token": access_token, "token_type": "bearer"},
        status_code=HTTPStatus.OK,
        message="Inicio de sesión exitoso",
        error=None,
    )


@router.post("/users/{id}/record", status_code=201, response_model=Response[object])
async def create_user_record(
    id: int,
    record: str = Form(...),
    medicines: str = Form(None),
    cares: str = Form(None),
    interventions: str = Form(None),
    vaccines: str = Form(None),
    attachments: Optional[List[UploadFile]] = File(None),
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    record_data = json.loads(record)
    medicines_data = json.loads(medicines) if medicines else []
    cares_data = json.loads(cares) if cares else []
    interventions_data = json.loads(interventions) if interventions else []
    vaccines_data = json.loads(vaccines) if vaccines else []

    record_to_save = MedicalRecord(**record_data)
    medicines_to_save = [
        MedicamentosPorUsuario(**medicine) for medicine in medicines_data
    ]
    cares_to_save = [CuidadosEnfermeriaPorUsuario(**care) for care in cares_data]
    interventions_to_save = [
        IntervencionesPorUsuario(**intervention) for intervention in interventions_data
    ]
    vaccines_to_save = [VacunasPorUsuario(**vaccine) for vaccine in vaccines_data]

    crud.save_user_medical_record(
        id,
        record_to_save,
        medicines_to_save,
        cares_to_save,
        interventions_to_save,
        vaccines_to_save,
        attachments,
    )

    return Response[object](
        data={},
        message="Historia clínica registrada de manera exitosa",
        status_code=201,
        error=None,
    )


@router.post(
    "/users/{id}/medical_record",
    status_code=201,
    response_model=Response[CreateUserMedicalRecordResponseDTO],
)
async def create_user_medical_record(
    id: int,
    record: CreateUserMedicalRecordCreateRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[CreateUserMedicalRecordResponseDTO]:
    record_to_save = MedicalRecord(**record.dict())
    saved_record = crud.create_user_medical_record(id, record_to_save)
    response_data = CreateUserMedicalRecordResponseDTO(**saved_record.__dict__)
    return Response[CreateUserMedicalRecordResponseDTO](
        data=response_data,
        message="Historia clínica creada con éxito",
        status_code=201,
        error=None,
    )


@router.post("/create", status_code=201, response_model=Response[CreateUserResponseDTO])
async def create_user(
    user: AuthorizedUserCreateRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[UserResponseDTO]:
    hashed_password = hash_password(user.password)
    user_to_save = AuthorizedUsers(**user.dict())
    user_to_save.password = hashed_password
    saved_user = crud.create_user(user_to_save)
    access_token = create_access_token(data={"sub": str(saved_user.id)})
    saved_user.token = access_token

    return Response[CreateUserResponseDTO](
        data=saved_user.__dict__,
        status_code=HTTPStatus.CREATED,
        message="User created successfully",
        error=None,
    )


@router.post("/medical_reports/", response_model=Response[ReporteClinicoResponse])
def create_reporte_clinico(
    reporte: ReporteClinicoCreate,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[ReporteClinicoResponse]:
    report_to_save = ReportesClinicos(**reporte.dict())
    resulting_report = crud.save_medical_report(report_to_save)
    return Response[ReporteClinicoResponse](
        data=ReporteClinicoResponse(**resulting_report.__dict__),
        message="Reporte clínico creado de manera exitosa",
        status_code=200,
        error=None,
    )


@router.post(
    "/reports/{id}/evolutions", response_model=Response[ClinicalEvolutionResponse]
)
def create_clinical_evolution(
    evolution: ClinicalEvolutionCreate,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[ClinicalEvolutionResponse]:
    report_to_save = EvolucionesClinicas(**evolution.dict())
    resulting_report = crud.save_clinical_evolution(report_to_save)
    return Response[ClinicalEvolutionResponse](
        data=ClinicalEvolutionResponse(**resulting_report.__dict__),
        message="Evolución clínica creada de manera exitosa",
        status_code=200,
        error=None,
    )


@router.post("/activities", response_model=Response[ActivitiesResponse])
def create_activity(
    activity: ActividadesGrupalesCreate,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[ActivitiesResponse]:
    activity_to_save = ActividadesGrupales(**activity.dict())
    resulting_activity = crud.save_activity(activity_to_save)
    return Response[ActivitiesResponse](
        data=ActivitiesResponse(**resulting_activity.__dict__),
        message="Actividad creada de manera exitosa",
        status_code=200,
        error=None,
    )


@router.patch("/users/{id}", status_code=200, response_model=Response[UserResponseDTO])
async def update_user(
    id: int,
    user: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    try:
        user_data = UserCreateRequestDTO.parse_raw(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user data: {str(e)}")

    user_to_save = User(**user_data.dict())

    saved_user = crud.update_user(id, user_to_save, photo)
    user_response = UserResponseDTO(**saved_user.__dict__)

    return Response[UserResponseDTO](
        data=user_response,
        status_code=HTTPStatus.OK,
        message="Usuario actualizado de manera exitosa",
        error=None,
    )


@router.patch("/user/treatment/{id}", status_code=200, response_model=Response[object])
async def update_treatment(
    id: int,
    treatment: MedicinesPerUserUpdateDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    treatment_to_update = MedicamentosPorUsuario(**treatment.__dict__)
    crud.update_medical_treatment(id, treatment_to_update)
    return Response[object](
        data={},
        status_code=HTTPStatus.OK,
        message="Medicamento actualizado de manera exitosa",
        error=None,
    )


@router.patch("/user/nursing/{id}", status_code=200, response_model=Response[object])
async def update_nursing(
    id: int,
    treatment: CaresPerUserUpdateDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    treatment_to_update = CuidadosEnfermeriaPorUsuario(**treatment.__dict__)
    crud.update_medical_nursing(id, treatment_to_update)
    return Response[object](
        data={},
        status_code=HTTPStatus.OK,
        message="Tratamiento actualizado de manera exitosa",
        error=None,
    )


@router.patch(
    "/user/intervention/{id}", status_code=200, response_model=Response[object]
)
async def update_intervention(
    id: int,
    treatment: InterventionsPerUserUpdateDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    treatment_to_update = IntervencionesPorUsuario(**treatment.__dict__)
    crud.update_medical_intervention(id, treatment_to_update)
    return Response[object](
        data={},
        status_code=HTTPStatus.OK,
        message="Intervención actualizada de manera exitosa",
        error=None,
    )


@router.patch("/user/vaccine/{id}", status_code=200, response_model=Response[object])
async def update_vaccine(
    id: int,
    treatment: VaccinesPerUserUpdateDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    treatment_to_update = VacunasPorUsuario(**treatment.__dict__)
    crud.update_medical_vaccine(id, treatment_to_update)
    return Response[object](
        data={},
        status_code=HTTPStatus.OK,
        message="Vacuna actualizada de manera exitosa",
        error=None,
    )


@router.patch(
    "/family_members/{id}",
    status_code=200,
    response_model=Response[FamilyMemberResponseDTO],
)
async def update_family_member(
    id: int,
    family_member_id: int,
    family_member: UpdateFamilyMemberRequestDTO,
    kinship: AssociateFamilyMemberRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    db_family_member = crud._get_family_member_by_id(family_member_id)
    if not db_family_member:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Acudiente no encontrado"
        )

    family_member_to_update = FamilyMember(**family_member.dict())

    family_member_updated = crud._update_family_member(
        user_id=id,
        family_member=family_member_to_update,
        kinship=kinship,
        db_family_member=db_family_member[0],
    )

    return Response[FamilyMemberResponseDTO](
        data=family_member_updated.__dict__,
        status_code=HTTPStatus.OK,
        message="Acudiente actualizado de manera exitosa",
        error=None,
    )


@router.patch(
    "/users/{id}/medical_record/{record_id}",
    status_code=200,
    response_model=Response[object],
)
async def update_user_medical_record(
    id: int,
    record_id: int,
    record: UpdateUserMedicalRecordRequestDTO,
    medicines: List[CreateUserAssociatedMedicinesRequestDTO],
    cares: List[CreateUserAssociatedCaresRequestDTO],
    interventions: List[CreateUserAssociatedInterventionsRequestDTO],
    vaccines: List[CreateUserAssociatedVaccinesRequestDTO],
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    update_data = record.dict(exclude_unset=True)
    medicines_to_save = [
        MedicamentosPorUsuario(**medicine.__dict__) for medicine in medicines
    ]
    cares_to_save = [CuidadosEnfermeriaPorUsuario(**care.__dict__) for care in cares]
    interventions_to_save = [
        IntervencionesPorUsuario(**intervention.__dict__)
        for intervention in interventions
    ]
    vaccines_to_save = [VacunasPorUsuario(**vaccine.__dict__) for vaccine in vaccines]
    crud.update_user_medical_record(
        id,
        record_id,
        update_data,
        medicines_to_save,
        cares_to_save,
        interventions_to_save,
        vaccines_to_save,
    )
    return Response[object](
        data={},
        message="Historia clínica actualizada con éxito",
        status_code=200,
        error=None,
    )


@router.patch(
    "/medical_reports/{reporte_id}", response_model=Response[ReporteClinicoResponse]
)
def update_reporte_clinico(
    reporte_id: int,
    reporte: ReporteClinicoUpdate,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[ReporteClinicoResponse]:
    report_to_update = ReportesClinicos(**reporte.__dict__)
    result = crud.update_medical_record(reporte_id, report_to_update)
    return Response[ReporteClinicoResponse](
        data=ReporteClinicoResponse(**result.__dict__),
        status_code=HTTPStatus.OK,
        message="Reporte clínico actualizado de manera exitosa",
        error=None,
    )


@router.patch(
    "/evolutions/{evolution_id}", response_model=Response[ClinicalEvolutionResponse]
)
def update_evolution(
    evolution_id: int,
    evolution: ClinicalEvolutionUpdate,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[ClinicalEvolutionResponse]:
    report_to_update = EvolucionesClinicas(**evolution.__dict__)
    result = crud.update_clinical_evolution(evolution_id, report_to_update)
    return Response[ClinicalEvolutionResponse](
        data=ClinicalEvolutionResponse(**result.__dict__),
        status_code=HTTPStatus.OK,
        message="Evolución clínica actualizada de manera exitosa",
        error=None,
    )


@router.patch("/activities/{id}", response_model=Response[ActivitiesResponse])
def update_activity(
    id: int,
    activity: ActividadesGrupalesUpdate,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[ActivitiesResponse]:
    activity_to_update = ActividadesGrupales(**activity.__dict__)
    result = crud.update_activity(id, activity_to_update)
    return Response[ActivitiesResponse](
        data=ActivitiesResponse(**result.__dict__),
        status_code=HTTPStatus.OK,
        message="Actividad actualizada de manera exitosa",
        error=None,
    )


@router.delete("/pagos/{id}", response_model=Response[None])
async def delete_payment(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[None]:
    crud.delete_payment(id)
    return Response[None](
        data=None,
        error=None,
        message="Pago eliminado de manera exitosa",
        status_code=HTTPStatus.NO_CONTENT,
    )


@router.delete("/users/{id}", status_code=200, response_model=Response[object])
async def delete_user(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_user(id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Usuario eliminado de manera exitosa",
        error=None,
    )


@router.delete("/family_members/{id}", status_code=200, response_model=Response[object])
async def delete_family_member(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_family_member(id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Acudiente eliminado de manera exitosa",
        error=None,
    )


@router.delete("/records/{id}", status_code=200, response_model=Response[object])
async def delete_record(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_user_medical_record(id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Historia clínica eliminada de manera exitosa",
        error=None,
    )


@router.delete(
    "/records/{id}/vaccine/{vaccine_id}",
    status_code=200,
    response_model=Response[object],
)
async def delete_vaccine(
    id: int,
    vaccine_id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_user_vaccine_by_record_id(id, vaccine_id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Vacuna eliminada de manera exitosa",
        error=None,
    )


@router.delete(
    "/records/{id}/medicine/{medicine_id}",
    status_code=200,
    response_model=Response[object],
)
async def delete_medicine(
    id: int,
    medicine_id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_user_medicines_by_record_id(id, medicine_id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Medicamento eliminado de manera exitosa",
        error=None,
    )


@router.delete(
    "/records/{id}/care/{care_id}",
    status_code=200,
    response_model=Response[object],
)
async def delete_care(
    id: int,
    care_id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_user_care_by_record_id(id, care_id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Cuidado eliminado de manera exitosa",
        error=None,
    )


@router.delete(
    "/records/{id}/intervention/{intervention_id}",
    status_code=200,
    response_model=Response[object],
)
async def delete_intervention(
    id: int,
    intervention_id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_user_intervention_by_record_id(id, intervention_id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Intervención eliminada de manera exitosa",
        error=None,
    )


@router.delete("/evolutions/{id}", status_code=200, response_model=Response[object])
async def delete_evolution(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    crud.delete_clinical_evolution(id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Reporte de evolución clínica eliminado con éxito",
        error=None,
    )


@router.delete("/reports/{id}", status_code=200, response_model=Response[object])
async def delete_report(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    crud.delete_medical_report(id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Reporte clínico eliminado con éxito",
        error=None,
    )


@router.delete(
    "/activities/{id}",
    status_code=200,
    response_model=Response[object],
)
async def delete_activity(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_activity(id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message="Actividad eliminada de manera exitosa",
        error=None,
    )


@router.post("/contratos/", response_model=Response[ContratoResponseDTO])
def crear_contrato(
    data: ContratoCreateDTO, db: Session = Depends(get_carelink_db)
) -> Response[ContratoResponseDTO]:
    try:
        contrato = Contratos(
            id_usuario=data.id_usuario,
            tipo_contrato=data.tipo_contrato,
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            facturar_contrato=data.facturar_contrato,
        )
        db.add(contrato)
        db.commit()
        db.refresh(contrato)

        # Obtener fechas de tiquetera y transporte
        fechas_tiquetera = set()
        fechas_transporte = set()
        servicios_db = []
        for servicio in data.servicios:
            servicio_contratado = ServiciosPorContrato(
                id_contrato=contrato.id_contrato,
                id_servicio=servicio.id_servicio,
                fecha=servicio.fecha,
                descripcion=servicio.descripcion,
                precio_por_dia=servicio.precio_por_dia,
            )
            db.add(servicio_contratado)
            db.commit()
            db.refresh(servicio_contratado)
            # Guardar fechas del servicio
            for f in servicio.fechas_servicio:
                fecha_servicio = FechasServicio(
                    id_servicio_contratado=servicio_contratado.id_servicio_contratado,
                    fecha=f.fecha,
                )
                db.add(fecha_servicio)
                db.commit()
                # Clasificar fechas
                if servicio.id_servicio == 1:
                    fechas_tiquetera.add(f.fecha)
                elif servicio.id_servicio == 2:
                    fechas_transporte.add(f.fecha)
            # Para la respuesta
            fechas_dto = [FechaServicioDTO(fecha=f.fecha) for f in servicio.fechas_servicio]
            servicios_db.append(
                ServicioContratoDTO(
                    id_servicio_contratado=servicio_contratado.id_servicio_contratado,
                    id_servicio=servicio.id_servicio,
                    fecha=servicio.fecha,
                    descripcion=servicio.descripcion,
                    precio_por_dia=servicio.precio_por_dia,
                    fechas_servicio=fechas_dto,
                )
            )

        # Procesar cronogramas de asistencia y transporte
        id_profesional_default = 1
        for fecha in fechas_tiquetera:
            # Crear o buscar cronograma de asistencia
            cronograma_existente = (
                db.query(CronogramaAsistencia)
                .filter(
                    CronogramaAsistencia.fecha == fecha,
                    CronogramaAsistencia.id_profesional == id_profesional_default
                )
                .first()
            )
            if not cronograma_existente:
                cronograma_asistencia = CronogramaAsistencia(
                    id_profesional=id_profesional_default,
                    fecha=fecha,
                    comentario=f"Generado automáticamente desde contrato {contrato.id_contrato}"
                )
                db.add(cronograma_asistencia)
                db.commit()
                db.refresh(cronograma_asistencia)
            else:
                cronograma_asistencia = cronograma_existente
            # Determinar si ese día requiere transporte
            requiere_transporte = fecha in fechas_transporte
            # Agregar paciente al cronograma
            paciente_cronograma = CronogramaAsistenciaPacientes(
                id_cronograma=cronograma_asistencia.id_cronograma,
                id_usuario=data.id_usuario,
                id_contrato=contrato.id_contrato,
                estado_asistencia="PENDIENTE",
                requiere_transporte=requiere_transporte,
                observaciones=None
            )
            db.add(paciente_cronograma)
            db.commit()
            db.refresh(paciente_cronograma)
            # Si requiere transporte, crear cronograma_transporte
            if requiere_transporte:
                cronograma_transporte = CronogramaTransporte(
                    id_cronograma_paciente=paciente_cronograma.id_cronograma_paciente,
                    direccion_recogida="Por definir",
                    direccion_entrega="Por definir",
                    hora_recogida=time(8, 0),
                    hora_entrega=time(17, 0),
                    estado="PENDIENTE",
                    observaciones="Generado automáticamente desde contrato"
                )
                db.add(cronograma_transporte)
                db.commit()

        db.commit()
        db.refresh(contrato)

        # Construir respuesta igual que obtener_contrato
        return Response[ContratoResponseDTO](
            data=ContratoResponseDTO(
                id_contrato=contrato.id_contrato,
                id_usuario=contrato.id_usuario,
                tipo_contrato=contrato.tipo_contrato,
                fecha_inicio=contrato.fecha_inicio,
                fecha_fin=contrato.fecha_fin,
                facturar_contrato=contrato.facturar_contrato,
                estado=contrato.estado,
                servicios=servicios_db,
            ),
            message="Contrato creado de manera exitosa",
            status_code=HTTPStatus.CREATED,
            error=None,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al crear contrato: {str(e)}"
        )


@router.get("/contratos/{contract_id}/factura", response_model=Response[FacturaOut])
async def list_contract_bill(
    contract_id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[FacturaOut]:
    bill = crud.get_contract_bill(contract_id)
    bill_response = FacturaOut.from_orm(bill)
    return Response[FacturaOut](
        data=bill_response,
        message="Factura listada",
        error=None,
        status_code=HTTPStatus.OK,
    )


@router.get("/contratos/{id_usuario}", response_model=List[ContratoResponseDTO])
def listar_contratos_por_usuario(
    id_usuario: int, db: Session = Depends(get_carelink_db)
):
    try:
        contratos = db.query(Contratos).filter(Contratos.id_usuario == id_usuario).all()

        if not contratos:
            return []

        result = []
        for contrato in contratos:
            servicios_db = (
                db.query(ServiciosPorContrato)
                .filter(ServiciosPorContrato.id_contrato == contrato.id_contrato)
                .all()
            )
            servicios = []
            for s in servicios_db:
                fechas = (
                    db.query(FechasServicio)
                    .filter(
                        FechasServicio.id_servicio_contratado
                        == s.id_servicio_contratado
                    )
                    .all()
                )
                fechas_dto = [FechaServicioDTO(fecha=f.fecha) for f in fechas]

                servicios.append(
                    ServicioContratoDTO(
                        id_servicio=s.id_servicio,
                        id_servicio_contratado=s.id_servicio_contratado,
                        fecha=s.fecha,
                        descripcion=s.descripcion,
                        precio_por_dia=s.precio_por_dia,
                        fechas_servicio=fechas_dto,
                    )
                )

            result.append(
                ContratoResponseDTO(
                    id_contrato=contrato.id_contrato,
                    id_usuario=id_usuario,
                    tipo_contrato=contrato.tipo_contrato,
                    fecha_inicio=contrato.fecha_inicio,
                    fecha_fin=contrato.fecha_fin,
                    facturar_contrato=contrato.facturar_contrato,
                    estado=contrato.estado,  # <-- Se agrega el campo estado
                    servicios=servicios,
                )
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al listar contratos: {str(e)}"
        )


@router.get("/contrato/{id_contrato}", response_model=ContratoResponseDTO)
def obtener_contrato(id_contrato: int, db: Session = Depends(get_carelink_db)):
    contrato = db.query(Contratos).filter(Contratos.id_contrato == id_contrato).first()

    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    servicios_db = (
        db.query(ServiciosPorContrato)
        .filter(ServiciosPorContrato.id_contrato == contrato.id_contrato)
        .all()
    )
    servicios = []
    for s in servicios_db:
        fechas = (
            db.query(FechasServicio)
            .filter(FechasServicio.id_servicio_contratado == s.id_servicio_contratado)
            .all()
        )
        fechas_dto = [FechaServicioDTO(fecha=f.fecha) for f in fechas]

        servicios.append(
            ServicioContratoDTO(
                id_servicio_contratado=s.id_servicio_contratado,
                id_servicio=s.id_servicio,
                fecha=s.fecha,
                descripcion=s.descripcion,
                precio_por_dia=s.precio_por_dia,
                fechas_servicio=fechas_dto,
            )
        )

    return ContratoResponseDTO(
        id_contrato=contrato.id_contrato,
        id_usuario=contrato.id_usuario,
        tipo_contrato=contrato.tipo_contrato,
        fecha_inicio=contrato.fecha_inicio,
        fecha_fin=contrato.fecha_fin,
        facturar_contrato=contrato.facturar_contrato,
        estado=contrato.estado,  # <-- Se agrega el campo estado
        servicios=servicios,
    )


@router.patch("/contrato/{id_contrato}")
def actualizar_contrato(
    id_contrato: int,
    data: ContratoUpdateDTO,
    db: Session = Depends(get_carelink_db),
):
    contrato = db.query(Contratos).filter(Contratos.id_contrato == id_contrato).first()

    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    try:
        # 🔴 Eliminar servicios anteriores del contrato (y sus fechas asociadas)
        servicios_anteriores = (
            db.query(ServiciosPorContrato)
            .filter(ServiciosPorContrato.id_contrato == contrato.id_contrato)
            .all()
        )

        for servicio_ant in servicios_anteriores:
            # Eliminar fechas asociadas
            db.query(FechasServicio).filter(
                FechasServicio.id_servicio_contratado
                == servicio_ant.id_servicio_contratado
            ).delete()

        # Eliminar servicios contratados
        db.query(ServiciosPorContrato).filter(
            ServiciosPorContrato.id_contrato == contrato.id_contrato
        ).delete()

        db.commit()

        # 🟢 Agregar nuevos servicios y fechas desde data.servicios
        for servicio in data.servicios:
            servicio_contratado = ServiciosPorContrato(
                id_contrato=contrato.id_contrato,
                id_servicio=servicio.id_servicio,
                fecha=servicio.fecha,
                descripcion=servicio.descripcion,
                precio_por_dia=servicio.precio_por_dia,
            )
            db.add(servicio_contratado)
            db.commit()
            db.refresh(servicio_contratado)

            for f in servicio.fechas_servicio:
                fecha_servicio = FechasServicio(
                    id_servicio_contratado=servicio_contratado.id_servicio_contratado,
                    fecha=f.fecha,
                )
                db.add(fecha_servicio)

        # ✏️ Actualizar otros atributos del contrato
        for attr, value in data.dict(exclude={"servicios"}, exclude_unset=True).items():
            setattr(contrato, attr, value)

        db.commit()
        db.refresh(contrato)

        return {"message": "Contrato actualizado correctamente"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar contrato: {str(e)}"
        )


@router.post("/servicios/{id_servicio}/fechas")
def crear_fechas_servicio(
    id_servicio: int,
    fechas: List[FechaServicioDTO],
    db: Session = Depends(get_carelink_db),
):
    for fecha in fechas:
        nueva_fecha = FechasServicio(
            id_servicio_contratado=id_servicio, fecha=fecha.fecha
        )
        db.add(nueva_fecha)
    db.commit()

    return {"message": "Fechas creadas correctamente"}


@router.patch("/servicios/{id_servicio_contratado}/fechas")
def actualizar_fechas_servicio(
    id_servicio_contratado: int,
    fechas: List[FechaServicioDTO],
    db: Session = Depends(get_carelink_db),
):
    servicio = (
        db.query(ServiciosPorContrato)
        .filter_by(id_servicio_contratado=id_servicio_contratado)
        .first()
    )

    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio contratado no encontrado")

    db.query(FechasServicio).filter_by(
        id_servicio_contratado=id_servicio_contratado
    ).delete()

    for f in fechas:
        nueva_fecha = FechasServicio(
            id_servicio_contratado=id_servicio_contratado, fecha=f.fecha
        )
        db.add(nueva_fecha)

    db.commit()
    return {"message": "Fechas actualizadas correctamente"}


@router.post("/pagos/")
def crear_pago(data: PagoCreateDTO, db: Session = Depends(get_carelink_db)):
    factura = db.query(Facturas).filter(Facturas.id_factura == data.id_factura).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    total_pagado = (
        db.query(func.sum(Pagos.valor))
        .filter(Pagos.id_factura == data.id_factura)
        .scalar()
        or 0
    )

    if total_pagado + data.valor > factura.total_factura:
        raise HTTPException(
            status_code=400,
            detail=f"El pago excede el total restante de la factura. Total restante: {factura.total_factura - total_pagado:.2f}",
        )

    nuevo_pago = Pagos(
        id_factura=data.id_factura,
        id_metodo_pago=data.id_metodo_pago,
        id_tipo_pago=data.id_tipo_pago,
        fecha_pago=data.fecha_pago,
        valor=data.valor,
    )
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return {"message": "Pago registrado correctamente", "id_pago": nuevo_pago.id_pago}


@router.get("/pagos/factura/{factura_id}", response_model=list[PagoResponseDTO])
def get_pagos_by_factura(factura_id: int, db: Session = Depends(get_carelink_db)):
    pagos = db.query(Pagos).filter(Pagos.id_factura == factura_id).all()
    return [PagoResponseDTO.from_orm(pago) for pago in pagos]


@router.delete("/pagos/{id_pago}")
def eliminar_pago(id_pago: int, db: Session = Depends(get_carelink_db)):
    pago = db.query(Pagos).filter(Pagos.id_pago == id_pago).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    db.delete(pago)
    db.commit()
    return {"message": "Pago eliminado correctamente"}


@router.post("/facturas/")
def create_factura(factura_data: FacturaCreate, db: Session = Depends(get_carelink_db)):
    contrato = (
        db.query(Contratos)
        .filter(Contratos.id_contrato == factura_data.id_contrato)
        .first()
    )
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    factura = Facturas(
        id_contrato=factura_data.id_contrato,
        fecha_emision=factura_data.fecha_emision,
        fecha_vencimiento=factura_data.fecha_vencimiento,
        total=factura_data.total,
    )
    db.add(factura)
    db.flush()

    for pago_data in factura_data.pagos:
        if (
            not db.query(MetodoPago)
            .filter_by(id_metodo_pago=pago_data.id_metodo_pago)
            .first()
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Método de pago {pago_data.id_metodo_pago} no existe",
            )
        if (
            not db.query(TipoPago)
            .filter_by(id_tipo_pago=pago_data.id_tipo_pago)
            .first()
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de pago {pago_data.id_tipo_pago} no existe",
            )

        pago = Pagos(
            id_factura=factura.id_factura,
            id_metodo_pago=pago_data.id_metodo_pago,
            id_tipo_pago=pago_data.id_tipo_pago,
            fecha_pago=pago_data.fecha_pago,
            valor=pago_data.valor,
        )
        db.add(pago)

    db.commit()
    return {"id_factura": factura.id_factura}


@router.post("/facturas/{factura_id}/pagos/")
def add_pago_to_factura(
    factura_id: int, pagos: List[PagoCreate], db: Session = Depends(get_carelink_db)
):
    factura = db.query(Facturas).filter(Facturas.id_factura == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    total_existente = sum(p.valor for p in factura.pagos)
    total_nuevo = sum(p.valor for p in pagos)
    if total_existente + total_nuevo > factura.total_factura:
        raise HTTPException(
            status_code=400, detail="Los pagos exceden el total de la factura"
        )

    for pago_data in pagos:
        if (
            not db.query(MetodoPago)
            .filter_by(id_metodo_pago=pago_data.id_metodo_pago)
            .first()
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Método de pago {pago_data.id_metodo_pago} no existe",
            )
        if (
            not db.query(TipoPago)
            .filter_by(id_tipo_pago=pago_data.id_tipo_pago)
            .first()
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de pago {pago_data.id_tipo_pago} no existe",
            )

        pago = Pagos(
            id_factura=factura_id,
            id_metodo_pago=pago_data.id_metodo_pago,
            id_tipo_pago=pago_data.id_tipo_pago,
            fecha_pago=pago_data.fecha_pago,
            valor=pago_data.valor,
        )
        db.add(pago)

    db.commit()
    return {"message": "Pagos agregados correctamente"}


@router.delete("/facturas/{factura_id}")
def delete_factura(factura_id: int, db: Session = Depends(get_carelink_db)):
    factura = db.query(Facturas).filter(Facturas.id_factura == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    db.delete(factura)
    db.commit()
    return {"message": "Factura eliminada correctamente"}


def get_facturas_by_contrato(db: Session, contrato_id: int):
    facturas = db.query(Facturas).filter(Facturas.id_contrato == contrato_id).all()
    if not facturas:
        raise HTTPException(
            status_code=404, detail=f"No hay facturas para el contrato {contrato_id}"
        )
    return facturas


@router.get("/contratos/{contrato_id}/facturas", response_model=list[FacturaOut])
def read_facturas_by_contrato(contrato_id: int, db: Session = Depends(get_carelink_db)):
    return get_facturas_by_contrato(db, contrato_id)


@router.post("/facturas/{contrato_id}", response_model=Response[FacturaOut])
def create_contract_bill(
    contrato_id: int, crud: CareLinkCrud = Depends(get_crud)
) -> Response[FacturaOut]:
    bill = crud.create_contract_bill(contrato_id)
    bill_response = FacturaOut(
        id_factura=bill.id_factura,
        id_contrato=bill.id_contrato,
        fecha_emision=bill.fecha_emision,
        total_factura=bill.total_factura,
    )
    return Response[FacturaOut](
        data=bill_response,
        status_code=HTTPStatus.CREATED,
        message="Factura asociada de manera exitosa",
        error=None,
    )


@router.delete("/contratos/{contrato_id}", response_model=Response[object])
def delete_contract_by_id(
    contrato_id: int,
    crud: CareLinkCrud = Depends(get_crud),
):
    crud.delete_contract_by_id(contrato_id)
    return Response[object](
        data={},
        status_code=HTTPStatus.NO_CONTENT,
        message=f"El contrato {contrato_id} se ha eliminado de manera exitosa",
        error=None,
    )


# ============================================================================
# ENDPOINTS DE CRONOGRAMA DE ASISTENCIA
# ============================================================================

@router.post("/cronograma_asistencia/crear", response_model=Response[CronogramaAsistenciaResponseDTO])
def crear_cronograma_asistencia(
    cronograma_data: CronogramaAsistenciaCreateDTO,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[CronogramaAsistenciaResponseDTO]:
    """
    Crea un nuevo cronograma de asistencia
    """
    try:
        # Verificar si ya existe un cronograma para esta fecha y profesional
        cronograma_existente = (
            db.query(CronogramaAsistencia)
            .filter(
                CronogramaAsistencia.fecha == cronograma_data.fecha,
                CronogramaAsistencia.id_profesional == cronograma_data.id_profesional
            )
            .first()
        )
        
        if cronograma_existente:
            # Si ya existe, retornar el existente
            return Response[CronogramaAsistenciaResponseDTO](
                data=CronogramaAsistenciaResponseDTO(
                    id_cronograma=cronograma_existente.id_cronograma,
                    id_profesional=cronograma_existente.id_profesional,
                    fecha=cronograma_existente.fecha,
                    comentario=cronograma_existente.comentario,
                    pacientes=[]
                ),
                status_code=HTTPStatus.OK,
                message="Cronograma existente recuperado",
                error=None,
            )
        
        # Crear nuevo cronograma
        nuevo_cronograma = CronogramaAsistencia(
            id_profesional=cronograma_data.id_profesional,
            fecha=cronograma_data.fecha,
            comentario=cronograma_data.comentario
        )
        
        db.add(nuevo_cronograma)
        db.commit()
        db.refresh(nuevo_cronograma)
        
        return Response[CronogramaAsistenciaResponseDTO](
            data=CronogramaAsistenciaResponseDTO(
                id_cronograma=nuevo_cronograma.id_cronograma,
                id_profesional=nuevo_cronograma.id_profesional,
                fecha=nuevo_cronograma.fecha,
                comentario=nuevo_cronograma.comentario,
                pacientes=[]
            ),
            status_code=HTTPStatus.CREATED,
            message="Cronograma creado exitosamente",
            error=None,
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear cronograma: {str(e)}"
        )


@router.post("/cronograma_asistencia/paciente/agregar", response_model=Response[CronogramaAsistenciaPacienteResponseDTO])
def agregar_paciente_cronograma(
    paciente_data: CronogramaAsistenciaPacienteCreateDTO,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[CronogramaAsistenciaPacienteResponseDTO]:
    """
    Agrega un paciente a un cronograma de asistencia existente
    """
    try:
        # Verificar si el paciente ya está en el cronograma
        paciente_existente = (
            db.query(CronogramaAsistenciaPacientes)
            .filter(
                CronogramaAsistenciaPacientes.id_cronograma == paciente_data.id_cronograma,
                CronogramaAsistenciaPacientes.id_usuario == paciente_data.id_usuario
            )
            .first()
        )
        
        if paciente_existente:
            raise HTTPException(
                status_code=400,
                detail="El paciente ya está registrado en este cronograma"
            )
        
        # Agregar paciente al cronograma
        nuevo_paciente = CronogramaAsistenciaPacientes(
            id_cronograma=paciente_data.id_cronograma,
            id_usuario=paciente_data.id_usuario,
            id_contrato=paciente_data.id_contrato,
            estado_asistencia=paciente_data.estado_asistencia,
            observaciones=paciente_data.observaciones
        )
        
        db.add(nuevo_paciente)
        db.commit()
        db.refresh(nuevo_paciente)
        
        return Response[CronogramaAsistenciaPacienteResponseDTO](
            data=CronogramaAsistenciaPacienteResponseDTO(
                id_cronograma_paciente=nuevo_paciente.id_cronograma_paciente,
                id_cronograma=nuevo_paciente.id_cronograma,
                id_usuario=nuevo_paciente.id_usuario,
                id_contrato=nuevo_paciente.id_contrato,
                estado_asistencia=nuevo_paciente.estado_asistencia,
                requiere_transporte=nuevo_paciente.requiere_transporte,
                observaciones=nuevo_paciente.observaciones
            ),
            status_code=HTTPStatus.CREATED,
            message="Paciente agregado al cronograma exitosamente",
            error=None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al agregar paciente al cronograma: {str(e)}"
        )


@router.get("/cronograma_asistencia/rango/{fecha_inicio}/{fecha_fin}", response_model=Response[List[CronogramaAsistenciaResponseDTO]])
def get_cronogramas_por_rango(
    fecha_inicio: str,
    fecha_fin: str,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[List[CronogramaAsistenciaResponseDTO]]:
    """
    Obtiene los cronogramas de asistencia en un rango de fechas
    """
    try:
        # Convertir fechas de string a date
        fecha_inicio_date = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_fin_date = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        
        # Consultar cronogramas en el rango
        cronogramas = (
            db.query(CronogramaAsistencia)
            .filter(
                CronogramaAsistencia.fecha >= fecha_inicio_date,
                CronogramaAsistencia.fecha <= fecha_fin_date
            )
            .all()
        )
        
        result = []
        for cronograma in cronogramas:
            # Obtener pacientes agendados para este cronograma
            pacientes_agendados = (
                db.query(CronogramaAsistenciaPacientes, User)
                .join(User, CronogramaAsistenciaPacientes.id_usuario == User.id_usuario)
                .filter(CronogramaAsistenciaPacientes.id_cronograma == cronograma.id_cronograma)
                .all()
            )
            
            pacientes_dto = []
            for paciente_agendado, usuario in pacientes_agendados:
                # Obtener información de transporte si existe
                transporte_info = None
                if paciente_agendado.requiere_transporte:
                    transporte = db.query(CronogramaTransporte).filter(
                        CronogramaTransporte.id_cronograma_paciente == paciente_agendado.id_cronograma_paciente
                    ).first()
                    if transporte:
                        transporte_info = {
                            "id_transporte": transporte.id_transporte,
                            "direccion_recogida": transporte.direccion_recogida,
                            "direccion_entrega": transporte.direccion_entrega,
                            "hora_recogida": str(transporte.hora_recogida) if transporte.hora_recogida else None,
                            "hora_entrega": str(transporte.hora_entrega) if transporte.hora_entrega else None,
                            "estado": transporte.estado,
                            "observaciones": transporte.observaciones
                        }
                pacientes_dto.append(
                    PacientePorFechaDTO(
                        id_cronograma_paciente=paciente_agendado.id_cronograma_paciente,
                        id_usuario=paciente_agendado.id_usuario,
                        id_contrato=paciente_agendado.id_contrato,
                        estado_asistencia=paciente_agendado.estado_asistencia,
                        requiere_transporte=paciente_agendado.requiere_transporte,
                        nombres=usuario.nombres,
                        apellidos=usuario.apellidos,
                        n_documento=usuario.n_documento,
                        transporte_info=transporte_info
                    )
                )
            
            result.append(
                CronogramaAsistenciaResponseDTO(
                    id_cronograma=cronograma.id_cronograma,
                    id_profesional=cronograma.id_profesional,
                    fecha=cronograma.fecha,
                    comentario=cronograma.comentario,
                    pacientes=pacientes_dto
                )
            )
        
        return Response[List[CronogramaAsistenciaResponseDTO]](
            data=result,
            status_code=HTTPStatus.OK,
            message="Cronogramas consultados exitosamente",
            error=None,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de fecha inválido: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/cronograma_asistencia/profesional/{id_profesional}", response_model=Response[List[CronogramaAsistenciaResponseDTO]])
def get_cronogramas_por_profesional(
    id_profesional: int,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[List[CronogramaAsistenciaResponseDTO]]:
    """
    Obtiene los cronogramas de asistencia de un profesional específico
    """
    try:
        # Consultar cronogramas del profesional
        cronogramas = (
            db.query(CronogramaAsistencia)
            .filter(CronogramaAsistencia.id_profesional == id_profesional)
            .all()
        )
        
        result = []
        for cronograma in cronogramas:
            # Obtener pacientes agendados para este cronograma
            pacientes_agendados = (
                db.query(CronogramaAsistenciaPacientes, User)
                .join(User, CronogramaAsistenciaPacientes.id_usuario == User.id_usuario)
                .filter(CronogramaAsistenciaPacientes.id_cronograma == cronograma.id_cronograma)
                .all()
            )
            
            pacientes_dto = []
            for paciente_agendado, usuario in pacientes_agendados:
                # Obtener información de transporte si existe
                transporte_info = None
                if paciente_agendado.requiere_transporte:
                    transporte = db.query(CronogramaTransporte).filter(
                        CronogramaTransporte.id_cronograma_paciente == paciente_agendado.id_cronograma_paciente
                    ).first()
                    if transporte:
                        transporte_info = {
                            "id_transporte": transporte.id_transporte,
                            "direccion_recogida": transporte.direccion_recogida,
                            "direccion_entrega": transporte.direccion_entrega,
                            "hora_recogida": str(transporte.hora_recogida) if transporte.hora_recogida else None,
                            "hora_entrega": str(transporte.hora_entrega) if transporte.hora_entrega else None,
                            "estado": transporte.estado,
                            "observaciones": transporte.observaciones
                        }
                pacientes_dto.append(
                    PacientePorFechaDTO(
                        id_cronograma_paciente=paciente_agendado.id_cronograma_paciente,
                        id_usuario=paciente_agendado.id_usuario,
                        id_contrato=paciente_agendado.id_contrato,
                        estado_asistencia=paciente_agendado.estado_asistencia,
                        requiere_transporte=paciente_agendado.requiere_transporte,
                        nombres=usuario.nombres,
                        apellidos=usuario.apellidos,
                        n_documento=usuario.n_documento,
                        transporte_info=transporte_info
                    )
                )
            
            result.append(
                CronogramaAsistenciaResponseDTO(
                    id_cronograma=cronograma.id_cronograma,
                    id_profesional=cronograma.id_profesional,
                    fecha=cronograma.fecha,
                    comentario=cronograma.comentario,
                    pacientes=pacientes_dto
                )
            )
        
        return Response[List[CronogramaAsistenciaResponseDTO]](
            data=result,
            status_code=HTTPStatus.OK,
            message="Cronogramas del profesional consultados exitosamente",
            error=None,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.patch("/cronograma_asistencia/paciente/{id_cronograma_paciente}/estado", response_model=Response[CronogramaAsistenciaPacienteResponseDTO])
def update_estado_asistencia(
    id_cronograma_paciente: int,
    estado_data: EstadoAsistenciaUpdateDTO,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[CronogramaAsistenciaPacienteResponseDTO]:
    """
    Actualiza el estado de asistencia de un paciente y guarda observaciones. 
    Si asiste o no asiste (sin justificación), descuenta día de tiquetera. 
    Si se agotan días, marca contrato como vencido y genera alerta.
    """
    try:
        paciente_cronograma = (
            db.query(CronogramaAsistenciaPacientes)
            .filter(CronogramaAsistenciaPacientes.id_cronograma_paciente == id_cronograma_paciente)
            .first()
        )
        if not paciente_cronograma:
            raise HTTPException(
                status_code=404,
                detail="Paciente no encontrado en el cronograma"
            )
        
        # 🔴 VALIDACIÓN: Solo se puede cambiar estado de registros "PENDIENTE"
        if paciente_cronograma.estado_asistencia != "PENDIENTE":
            raise HTTPException(
                status_code=400,
                detail=f"No se puede cambiar el estado de un paciente con estado '{paciente_cronograma.estado_asistencia}'. Solo se puede modificar registros con estado 'PENDIENTE'."
            )
        
        estados_validos = ["PENDIENTE", "ASISTIO", "NO_ASISTIO", "CANCELADO"]
        if estado_data.estado_asistencia not in estados_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Estado inválido. Estados válidos: {', '.join(estados_validos)}"
            )
        # Guardar observaciones
        paciente_cronograma.observaciones = estado_data.observaciones
        paciente_cronograma.estado_asistencia = estado_data.estado_asistencia
        db.commit()
        db.refresh(paciente_cronograma)
        
        # 🔴 LÓGICA DE DESCUENTO DE DÍAS DE TIQUETERA
        # Se descuenta día tanto si ASISTE como si NO ASISTE (sin justificación)
        if estado_data.estado_asistencia in ["ASISTIO", "NO_ASISTIO"]:
            contrato = db.query(Contratos).filter(Contratos.id_contrato == paciente_cronograma.id_contrato).first()
            if contrato:
                # Contar días consumidos (asistencias + no asistencias)
                total_dias_consumidos = db.query(CronogramaAsistenciaPacientes).filter(
                    CronogramaAsistenciaPacientes.id_contrato == contrato.id_contrato,
                    CronogramaAsistenciaPacientes.estado_asistencia.in_(["ASISTIO", "NO_ASISTIO"])
                ).count()
                
                # Contar total de días de la tiquetera (servicio 1)
                total_tiquetera = db.query(CronogramaAsistenciaPacientes).filter(
                    CronogramaAsistenciaPacientes.id_contrato == contrato.id_contrato
                ).count()
                
                # Si se agotaron todos los días, marcar contrato como vencido
                if total_dias_consumidos >= total_tiquetera:
                    contrato.estado = "VENCIDO"
                    db.commit()
                    # Aquí puedes agregar lógica para generar una alerta al profesional
        response_dto = CronogramaAsistenciaPacienteResponseDTO(
            id_cronograma_paciente=paciente_cronograma.id_cronograma_paciente,
            id_cronograma=paciente_cronograma.id_cronograma,
            id_usuario=paciente_cronograma.id_usuario,
            id_contrato=paciente_cronograma.id_contrato,
            estado_asistencia=paciente_cronograma.estado_asistencia,
            observaciones=paciente_cronograma.observaciones
        )
        return Response[CronogramaAsistenciaPacienteResponseDTO](
            data=response_dto,
            status_code=HTTPStatus.OK,
            message="Estado de asistencia actualizado exitosamente",
            error=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/cronograma_asistencia/paciente/{id_cronograma_paciente}/reagendar", response_model=Response[CronogramaAsistenciaPacienteResponseDTO])
def reagendar_asistencia_paciente(
    id_cronograma_paciente: int,
    estado_data: EstadoAsistenciaUpdateDTO,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[CronogramaAsistenciaPacienteResponseDTO]:
    """
    Reagenda la asistencia de un paciente SOLO si existe justificación (observaciones) y nueva fecha.
    """
    try:
        paciente_cronograma = (
            db.query(CronogramaAsistenciaPacientes)
            .filter(CronogramaAsistenciaPacientes.id_cronograma_paciente == id_cronograma_paciente)
            .first()
        )
        if not paciente_cronograma:
            raise HTTPException(
                status_code=404,
                detail="Paciente no encontrado en el cronograma"
            )
        
        # 🔴 VALIDACIÓN POR REGISTRO INDIVIDUAL Y ESTADO
        # Solo se puede reagendar si el estado es "PENDIENTE"
        if paciente_cronograma.estado_asistencia in ["REAGENDADO", "ASISTIO", "NO_ASISTIO", "CANCELADO"]:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede reagendar un paciente que ya tiene estado '{paciente_cronograma.estado_asistencia}' en esta fecha. Solo se puede reagendar si el estado es 'PENDIENTE'."
            )
        
        if not estado_data.observaciones or not estado_data.observaciones.strip():
            raise HTTPException(
                status_code=400,
                detail="No se puede reagendar sin justificación en observaciones."
            )
        if not estado_data.nueva_fecha:
            raise HTTPException(
                status_code=400,
                detail="Debe seleccionar una nueva fecha para reagendar."
            )
        
        # 🔴 PASO 1: Obtener el id_profesional del cronograma original
        cronograma_original = db.query(CronogramaAsistencia).filter_by(
            id_cronograma=paciente_cronograma.id_cronograma
        ).first()
        id_profesional = cronograma_original.id_profesional
        
        # 🔴 PASO 2: Buscar o crear cronograma para la nueva fecha
        cronograma_nuevo = db.query(CronogramaAsistencia).filter_by(
            id_profesional=id_profesional,
            fecha=estado_data.nueva_fecha
        ).first()
        
        if not cronograma_nuevo:
            cronograma_nuevo = CronogramaAsistencia(
                id_profesional=id_profesional,
                fecha=estado_data.nueva_fecha
            )
            db.add(cronograma_nuevo)
            db.commit()
            db.refresh(cronograma_nuevo)
        
        # 🔴 PASO 3: Verificar que no esté ya agendado para la nueva fecha
        agendado_existente = db.query(CronogramaAsistenciaPacientes).filter_by(
            id_cronograma=cronograma_nuevo.id_cronograma,
            id_usuario=paciente_cronograma.id_usuario
        ).first()
        
        if agendado_existente:
            raise HTTPException(
                status_code=400,
                detail="El paciente ya está agendado para esta fecha."
            )
        
        # 🔴 PASO 4: Crear nuevo registro para la nueva fecha
        nuevo_paciente_cronograma = CronogramaAsistenciaPacientes(
            id_cronograma=cronograma_nuevo.id_cronograma,
            id_usuario=paciente_cronograma.id_usuario,
            id_contrato=paciente_cronograma.id_contrato,
            estado_asistencia="PENDIENTE",
            observaciones=""
        )
        db.add(nuevo_paciente_cronograma)
        db.commit()
        db.refresh(nuevo_paciente_cronograma)
        
        # 🔴 PASO 5: SOLO DESPUÉS de crear exitosamente el nuevo registro, cambiar estado del original
        paciente_cronograma.estado_asistencia = "REAGENDADO"
        paciente_cronograma.observaciones = estado_data.observaciones
        db.commit()
        
        response_dto = CronogramaAsistenciaPacienteResponseDTO(
            id_cronograma_paciente=nuevo_paciente_cronograma.id_cronograma_paciente,
            id_cronograma=nuevo_paciente_cronograma.id_cronograma,
            id_usuario=nuevo_paciente_cronograma.id_usuario,
            id_contrato=nuevo_paciente_cronograma.id_contrato,
            estado_asistencia=nuevo_paciente_cronograma.estado_asistencia,
            observaciones=nuevo_paciente_cronograma.observaciones
        )
        return Response[CronogramaAsistenciaPacienteResponseDTO](
            data=response_dto,
            status_code=HTTPStatus.OK,
            message="Paciente reagendado exitosamente",
            error=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


# ============================================================================
# ENDPOINTS DE CRONOGRAMA DE TRANSPORTE
# ============================================================================

@router.post("/transporte/crear", response_model=Response[CronogramaTransporteResponseDTO])
def crear_cronograma_transporte(
    transporte_data: CronogramaTransporteCreateDTO,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[CronogramaTransporteResponseDTO]:
    """
    Crea un registro de transporte para un paciente en el cronograma
    """
    try:
        # Verificar que el cronograma_paciente existe
        cronograma_paciente = db.query(CronogramaAsistenciaPacientes).filter(
            CronogramaAsistenciaPacientes.id_cronograma_paciente == transporte_data.id_cronograma_paciente
        ).first()
        
        if not cronograma_paciente:
            raise HTTPException(
                status_code=404,
                detail="Paciente no encontrado en el cronograma"
            )
        
        # Verificar que no existe ya un registro de transporte
        transporte_existente = db.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_cronograma_paciente == transporte_data.id_cronograma_paciente
        ).first()
        
        if transporte_existente:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un registro de transporte para este paciente en esta fecha"
            )
        
        # Crear el registro de transporte
        nuevo_transporte = CronogramaTransporte(
            id_cronograma_paciente=transporte_data.id_cronograma_paciente,
            direccion_recogida=transporte_data.direccion_recogida,
            direccion_entrega=transporte_data.direccion_entrega,
            hora_recogida=transporte_data.hora_recogida,
            hora_entrega=transporte_data.hora_entrega,
            observaciones=transporte_data.observaciones
        )
        
        db.add(nuevo_transporte)
        # ACTUALIZAR requiere_transporte a True
        cronograma_paciente.requiere_transporte = True
        db.commit()
        db.refresh(nuevo_transporte)
        
        response_dto = CronogramaTransporteResponseDTO.from_orm(nuevo_transporte)
        return Response[CronogramaTransporteResponseDTO](
            data=response_dto,
            status_code=HTTPStatus.CREATED,
            message="Cronograma de transporte creado exitosamente",
            error=None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.patch("/transporte/{id_transporte}", response_model=Response[CronogramaTransporteResponseDTO])
def actualizar_cronograma_transporte(
    id_transporte: int,
    transporte_data: CronogramaTransporteUpdateDTO,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[CronogramaTransporteResponseDTO]:
    """
    Actualiza un registro de transporte
    """
    try:
        transporte = db.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_transporte == id_transporte
        ).first()
        
        if not transporte:
            raise HTTPException(
                status_code=404,
                detail="Registro de transporte no encontrado"
            )
        
        # Actualizar campos
        for field, value in transporte_data.dict(exclude_unset=True).items():
            setattr(transporte, field, value)
        
        db.commit()
        db.refresh(transporte)
        
        response_dto = CronogramaTransporteResponseDTO.from_orm(transporte)
        return Response[CronogramaTransporteResponseDTO](
            data=response_dto,
            status_code=HTTPStatus.OK,
            message="Cronograma de transporte actualizado exitosamente",
            error=None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/transporte/ruta/{fecha}", response_model=Response[RutaDiariaResponseDTO])
def obtener_ruta_transporte_diaria(
    fecha: str,
    id_profesional: int,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[RutaDiariaResponseDTO]:
    """
    Obtiene la ruta de transporte para una fecha específica
    """
    try:
        fecha_date = datetime.strptime(fecha, "%Y-%m-%d").date()
        
        # Obtener todos los pacientes que requieren transporte para esa fecha
        pacientes_transporte = (
            db.query(CronogramaAsistenciaPacientes, CronogramaTransporte, User)
            .join(CronogramaTransporte, CronogramaAsistenciaPacientes.id_cronograma_paciente == CronogramaTransporte.id_cronograma_paciente, isouter=True)
            .join(User, CronogramaAsistenciaPacientes.id_usuario == User.id_usuario)
            .join(CronogramaAsistencia, CronogramaAsistenciaPacientes.id_cronograma == CronogramaAsistencia.id_cronograma)
            .filter(
                CronogramaAsistencia.fecha == fecha_date,
                CronogramaAsistencia.id_profesional == id_profesional,
                CronogramaAsistenciaPacientes.requiere_transporte == True
            )
            .all()
        )
        
        rutas = []
        total_pendientes = 0
        total_realizados = 0
        total_cancelados = 0
        
        for paciente, transporte, usuario in pacientes_transporte:
            estado = transporte.estado if transporte else "PENDIENTE"
            
            if estado == "PENDIENTE":
                total_pendientes += 1
            elif estado == "REALIZADO":
                total_realizados += 1
            elif estado == "CANCELADO":
                total_cancelados += 1
            
            rutas.append(
                RutaTransporteResponseDTO(
                    id_transporte=transporte.id_transporte if transporte else 0,
                    id_cronograma_paciente=paciente.id_cronograma_paciente,
                    id_usuario=usuario.id_usuario,
                    nombres=usuario.nombres,
                    apellidos=usuario.apellidos,
                    n_documento=usuario.n_documento,
                    direccion_recogida=transporte.direccion_recogida if transporte else None,
                    direccion_entrega=transporte.direccion_entrega if transporte else None,
                    hora_recogida=transporte.hora_recogida if transporte else None,
                    hora_entrega=transporte.hora_entrega if transporte else None,
                    estado=estado,
                    observaciones=transporte.observaciones if transporte else None
                )
            )
        
        # Ordenar rutas por hora de recogida
        rutas.sort(key=lambda x: x.hora_recogida if x.hora_recogida else time(23, 59))
        
        response_dto = RutaDiariaResponseDTO(
            fecha=fecha,
            id_profesional=id_profesional,
            rutas=rutas,
            total_pacientes=len(rutas),
            total_pendientes=total_pendientes,
            total_realizados=total_realizados,
            total_cancelados=total_cancelados
        )
        
        return Response[RutaDiariaResponseDTO](
            data=response_dto,
            status_code=HTTPStatus.OK,
            message="Ruta de transporte consultada exitosamente",
            error=None,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de fecha inválido: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/transporte/paciente/{id_cronograma_paciente}", response_model=Response[CronogramaTransporteResponseDTO])
def obtener_transporte_paciente(
    id_cronograma_paciente: int,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[CronogramaTransporteResponseDTO]:
    """
    Obtiene la información de transporte de un paciente específico
    """
    try:
        transporte = db.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_cronograma_paciente == id_cronograma_paciente
        ).first()
        
        if not transporte:
            raise HTTPException(
                status_code=404,
                detail="No se encontró información de transporte para este paciente"
            )
        
        response_dto = CronogramaTransporteResponseDTO.from_orm(transporte)
        return Response[CronogramaTransporteResponseDTO](
            data=response_dto,
            status_code=HTTPStatus.OK,
            message="Información de transporte consultada exitosamente",
            error=None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.delete("/transporte/{id_transporte}", response_model=Response[None])
def eliminar_cronograma_transporte(
    id_transporte: int,
    db: Session = Depends(get_carelink_db),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[None]:
    """
    Elimina un registro de transporte
    """
    try:
        transporte = db.query(CronogramaTransporte).filter(
            CronogramaTransporte.id_transporte == id_transporte
        ).first()
        
        if not transporte:
            raise HTTPException(
                status_code=404,
                detail="Registro de transporte no encontrado"
            )
        
        db.delete(transporte)
        db.commit()
        
        return Response[None](
            data=None,
            status_code=HTTPStatus.NO_CONTENT,
            message="Cronograma de transporte eliminado exitosamente",
            error=None,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
