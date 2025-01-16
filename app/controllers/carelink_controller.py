from app.crud.carelink_crud import CareLinkCrud
from app.database.connection import get_carelink_db
from app.dto.v1.response.generic_response import Response
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from functools import lru_cache
from http import HTTPStatus
from sqlalchemy.orm import Session
from typing import Any

token_auth_scheme = HTTPBearer()

router = APIRouter()


@lru_cache()
def get_crud(
    carelink_db: Session = Depends(get_carelink_db),
):
    return CareLinkCrud(carelink_db)


@router.get("/")
async def list(crud: CareLinkCrud = Depends(get_crud)):
    return Response[Any](
        data={"Hola": "La buena"},
        status_code=HTTPStatus.OK,
        error=None,
        message="Holi gordo",
    )
