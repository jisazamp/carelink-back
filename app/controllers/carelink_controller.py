from app.crud.carelink_crud import CareLinkCrud
from app.database.connection import get_carelink_db
from app.dto.v1.request.user_request_dto import UserCreateRequestDTO
from app.dto.v1.response.generic_response import Response
from app.dto.v1.response.user import UserResponseDTO, UserUpdateRequestDTO
from app.models.user import User
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
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
