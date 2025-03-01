from app.crud.carelink_crud import CareLinkCrud
from app.database.connection import get_carelink_db
from app.dto.v1.request.family_member_create_request_dto import (
    AssociateFamilyMemberRequestDTO,
    CreateFamilyMemberRequestDTO,
    UpdateFamilyMemberRequestDTO,
)
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
from app.dto.v1.response.cares_per_user import CaresPerUserResponseDTO
from app.dto.v1.response.create_user import CreateUserResponseDTO
from app.dto.v1.request.user_login_request_dto import UserLoginRequestDTO
from app.dto.v1.response.create_user_medical_record import (
    CreateUserMedicalRecordResponseDTO,
)
from app.dto.v1.response.family_member import FamilyMemberResponseDTO
from app.dto.v1.response.generic_response import Response
from app.dto.v1.response.interventions_per_user import InterventionsPerUserResponseDTO
from app.dto.v1.response.medicines_per_user import MedicinesPerUserResponseDTO
from app.dto.v1.response.user_info import UserInfo
from app.dto.v1.response.user import UserResponseDTO, UserUpdateRequestDTO
from app.dto.v1.response.family_members_by_user import FamilyMembersByUserResponseDTO
from app.dto.v1.response.vaccines_per_user import VaccinesPerUserResponseDTO
from app.models.authorized_users import AuthorizedUsers
from app.models.cares_per_user import CuidadosEnfermeriaPorUsuario
from app.models.family_member import FamilyMember
from app.models.interventions_per_user import IntervencionesPorUsuario
from app.models.medical_record import MedicalRecord
from app.models.medicines_per_user import MedicamentosPorUsuario
from app.models.user import User
from app.models.vaccines import VacunasPorUsuario
from app.security.jwt_utilities import (
    decode_access_token,
    create_access_token,
    hash_password,
)
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import lru_cache
from http import HTTPStatus
from sqlalchemy.orm import Session
from typing import List


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
        data=users_list, status_code=HTTPStatus.OK, message="Success", error=None
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
        data=user_response, status_code=HTTPStatus.OK, message="Success", error=None
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
        message="Family members retrieved successfuly",
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
        message="Family member retrieved successfuly",
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
        message="Family members retrieved successfuly",
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
        data=result, message="Success", status_code=201, error=None
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


@router.post("/users", status_code=201, response_model=Response[UserResponseDTO])
async def create_users(
    user: UserCreateRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[UserResponseDTO]:
    user_to_save = User(**user.dict())
    saved_user = crud.save_user(user_to_save)
    user_response = UserResponseDTO(**saved_user.__dict__)

    return Response[UserResponseDTO](
        data=user_response,
        status_code=HTTPStatus.CREATED,
        message="User created successfully",
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
        message="Family member created successfully",
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
        message="Login successful",
        error=None,
    )


@router.post("/users/{id}/record", status_code=201, response_model=Response[object])
async def create_user_record(
    id: int,
    record: CreateUserMedicalRecordCreateRequestDTO,
    medicines: List[CreateUserAssociatedMedicinesRequestDTO],
    cares: List[CreateUserAssociatedCaresRequestDTO],
    interventions: List[CreateUserAssociatedInterventionsRequestDTO],
    vaccines: List[CreateUserAssociatedVaccinesRequestDTO],
    crud: CareLinkCrud = Depends(get_crud),
) -> Response[object]:
    record_to_save = MedicalRecord(**record.__dict__)
    medicines_to_save = [
        MedicamentosPorUsuario(**medicine.__dict__) for medicine in medicines
    ]
    cares_to_save = [CuidadosEnfermeriaPorUsuario(**care.__dict__) for care in cares]
    interventions_to_save = [
        IntervencionesPorUsuario(**intervention.__dict__)
        for intervention in interventions
    ]
    vaccines_to_save = [VacunasPorUsuario(**vaccine.__dict__) for vaccine in vaccines]
    crud.save_user_medical_record(
        id,
        record_to_save,
        medicines_to_save,
        cares_to_save,
        interventions_to_save,
        vaccines_to_save,
    )
    return Response[object](data={}, message="Success", status_code=201, error=None)


@router.post(
    "/users/{id}/medical_record",
    status_code=201,
    response_model=Response[CreateUserMedicalRecordResponseDTO],
)
async def create_user_medical_record(
    id: int,
    record: CreateUserMedicalRecordCreateRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
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


@router.patch("/users/{id}", status_code=200, response_model=Response[UserResponseDTO])
async def update_user(
    id: int,
    user: UserUpdateRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    user_to_update = User(**user.dict())
    updated_user = crud.update_user(id, user_to_update)
    return Response[UserResponseDTO](
        data=updated_user.__dict__,
        status_code=HTTPStatus.OK,
        message="Usuario actualizado",
        error=None,
    )


@router.patch(
    "/family_members/{id}",
    status_code=200,
    response_model=Response[FamilyMemberResponseDTO],
)
async def update_family_member(
    id: int,
    family_member: UpdateFamilyMemberRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
):
    family_member_to_update = FamilyMember(**family_member.dict())
    family_member_updated = crud.update_family_member(id, family_member_to_update)
    return Response[FamilyMemberResponseDTO](
        data=family_member_updated.__dict__, status_code=HTTPStatus.OK
    )


@router.patch(
    "/users/{id}/medical_record/{record_id}",
    status_code=200,
    response_model=Response[CreateUserMedicalRecordResponseDTO],
)
async def update_user_medical_record(
    id: int,
    record_id: int,
    record: UpdateUserMedicalRecordRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
) -> Response[CreateUserMedicalRecordResponseDTO]:
    update_data = record.dict(exclude_unset=True)
    updated_record = crud.update_user_medical_record(id, record_id, update_data)
    response_data = CreateUserMedicalRecordResponseDTO(**updated_record.__dict__)
    return Response[CreateUserMedicalRecordResponseDTO](
        data=response_data,
        message="Historia clínica actualizada con éxito",
        status_code=200,
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
        data={}, status_code=HTTPStatus.NO_CONTENT, message="", error=None
    )


@router.delete("/family_members/{id}", status_code=200, response_model=Response[object])
async def delete_family_member(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_family_member(id)
    return Response[object](
        data={}, status_code=HTTPStatus.NO_CONTENT, message="", error=None
    )


@router.delete("/records/{id}", status_code=200, response_model=Response[object])
async def delete_record(
    id: int,
    crud: CareLinkCrud = Depends(get_crud),
    _: AuthorizedUsers = Depends(get_current_user),
) -> Response[object]:
    crud.delete_user_medical_record(id)
    return Response[object](
        data={}, status_code=HTTPStatus.NO_CONTENT, message="", error=None
    )
