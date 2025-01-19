from app.crud.carelink_crud import CareLinkCrud
from app.database.connection import get_carelink_db
from app.dto.v1.request.user_create_request_dto import UserCreateRequestDTO
from app.dto.v1.response.create_user import CreateUserResponseDTO
from app.dto.v1.request.user_login_request_dto import UserLoginRequestDTO
from app.dto.v1.response.generic_response import Response
from app.dto.v1.response.user_info import UserInfo
from app.dto.v1.response.user import UserResponseDTO, UserUpdateRequestDTO
from app.models.authorized_users import AuthorizedUsers
from app.models.user import User
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
from typing import Any, List


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
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    user = crud.list_user_by_user_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users", response_model=Response[List[UserResponseDTO]])
async def list_users(
    crud: CareLinkCrud = Depends(get_crud),
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
) -> Response[UserResponseDTO]:
    user = crud.list_user_by_user_id(id)
    return Response[UserResponseDTO](
        data=user.__dict__, status_code=HTTPStatus.OK, message="Success", error=None
    )


@router.post("/users", status_code=201, response_model=Response[UserResponseDTO])
async def create_users(
    user: UserCreateRequestDTO,
    crud: CareLinkCrud = Depends(get_crud),
) -> Response[UserResponseDTO]:
    user_to_save = User(**user.dict())
    saved_user = crud.save_user(user_to_save)

    return Response[UserResponseDTO](
        data=saved_user.__dict__,
        status_code=HTTPStatus.CREATED,
        message="User created successfully",
        error=None,
    )


@router.patch("/users/{id}", status_code=200, response_model=Response[UserResponseDTO])
async def update_user(
    id: int, user: UserUpdateRequestDTO, crud: CareLinkCrud = Depends(get_crud)
):
    user_to_update = User(**user.dict())
    updated_user = crud.update_user(id, user_to_update)
    return Response[UserResponseDTO](
        data=updated_user.__dict__, status_code=HTTPStatus.OK
    )


@router.delete("/users/{id}", status_code=200, response_model=Response[object])
async def delete_user(
    id: int, crud: CareLinkCrud = Depends(get_crud)
) -> Response[object]:
    crud.delete_user(id)
    return Response[object](data={}, status_code=HTTPStatus.NO_CONTENT)


@router.post("/login", response_model=Response[dict])
async def login_user(
    login_data: UserLoginRequestDTO, crud: CareLinkCrud = Depends(get_crud)
) -> Response[dict]:
    user = crud.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": user.id})
    return Response[dict](
        data={"access_token": access_token, "token_type": "bearer"},
        status_code=HTTPStatus.OK,
        message="Login successful",
        error=None,
    )


@router.post("/create", status_code=201, response_model=Response[CreateUserResponseDTO])
async def create_user(
    user: UserCreateRequestDTO,
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
