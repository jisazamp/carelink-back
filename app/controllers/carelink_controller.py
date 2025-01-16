from app.crud.carelink_crud import CareLinkCrud
from app.database.connection import get_carelink_db
from app.dto.v1.response.generic_response import Response
from app.dto.v1.response.user import UserResponseDTO
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


@router.get("/", response_model=Response[List[UserResponseDTO]])
async def list(
    crud: CareLinkCrud = Depends(get_crud),
) -> Response[List[UserResponseDTO]]:
    users = crud.list()
    return Response[List[UserResponseDTO]](
        data=users, status_code=HTTPStatus.OK, message="Hola", error=None
    )
