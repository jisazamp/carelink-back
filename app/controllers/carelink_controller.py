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
from app.dto.v1.response.contracts import (
    ContratoResponseDTO,
    FacturaOut,
    FechaServicioDTO,
    ServicioContratoDTO,
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
import json


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


@router.post("/calcular/factura", response_model=Response[float])
def calculate_partial_bill(
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

        db.commit()
        contract_response_dto: ContratoResponseDTO = ContratoResponseDTO.from_orm(
            contrato
        )
        return Response[ContratoResponseDTO](
            data=contract_response_dto,
            message="Contrato creado de manera exitosa",
            status_code=HTTPStatus.CREATED,
            error=None,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al crear contrato: {str(e)}"
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

    for attr, value in data.dict(exclude_unset=True).items():
        setattr(contrato, attr, value)

    try:
        db.commit()
        db.refresh(contrato)
        return {"message": "Contrato actualizado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar contrato: {str(e)}"
        )


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
