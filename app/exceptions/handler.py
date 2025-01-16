from http import HTTPStatus
import logging

from app.exceptions.exceptions_classes import (
    BusinessLogicError,
    EntityNotFoundError,
    SecurityError,
)
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.dto.v1.response.generic_response import Response


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        jsonable_encoder(
            Response[str](
                message="Invalid data",
                error=jsonable_encoder(exc.errors()),
                status_code=HTTPStatus.BAD_REQUEST,
            )
        ),
        status_code=HTTPStatus.BAD_REQUEST,
    )


async def entity_not_found_error_handler(request: Request, exc: EntityNotFoundError):
    logging.exception(exec)
    return JSONResponse(
        jsonable_encoder(
            Response[str](
                message="Entity not found",
                error=[str(exc)],
                status_code=HTTPStatus.NOT_FOUND,
            )
        ),
        status_code=HTTPStatus.NOT_FOUND,
    )


async def business_logic_error_handler(request: Request, exc: BusinessLogicError):
    logging.exception(exec)
    return JSONResponse(
        jsonable_encoder(
            Response[str](
                message="Invalid request",
                error=[str(exc)],
                status_code=HTTPStatus.BAD_REQUEST,
            )
        ),
        status_code=HTTPStatus.BAD_REQUEST,
    )


async def security_error_handler(request: Request, exc: SecurityError):
    logging.exception(exec)
    return JSONResponse(
        jsonable_encoder(
            Response[str](
                message="Unauthorized",
                error=[str(exc)],
                status_code=HTTPStatus.UNAUTHORIZED,
            )
        ),
        status_code=HTTPStatus.UNAUTHORIZED,
    )


async def http_error_handler(request: Request, exc: HTTPException):
    logging.exception(exec)
    return JSONResponse(
        jsonable_encoder(
            Response[str](
                message=exc.detail, error=[str(exc.detail)], status_code=exc.status_code
            )
        ),
        status_code=exc.status_code,
    )
