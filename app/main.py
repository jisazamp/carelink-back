from app.controllers import carelink_controller
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from app.exceptions.exceptions_classes import (
    BusinessLogicError,
    EntityNotFoundError,
    SecurityError,
)
from app.exceptions.handler import (
    business_logic_error_handler,
    entity_not_found_error_handler,
    http_error_handler,
    request_validation_error_handler,
    security_error_handler,
)

app = FastAPI(title="CareLink API")

app.add_exception_handler(
    exc_class_or_status_code=RequestValidationError,
    handler=request_validation_error_handler,
)

app.add_exception_handler(
    exc_class_or_status_code=EntityNotFoundError, handler=entity_not_found_error_handler
)

app.add_exception_handler(
    exc_class_or_status_code=BusinessLogicError, handler=business_logic_error_handler
)

app.add_exception_handler(
    exc_class_or_status_code=SecurityError, handler=security_error_handler
)

app.add_exception_handler(
    exc_class_or_status_code=HTTPException, handler=http_error_handler
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(carelink_controller.router, prefix="/api", tags=["CareLink"])
