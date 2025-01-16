from typing import Any, Generic, TypeVar, List

from pydantic import validator
from pydantic.generics import GenericModel

DataT = TypeVar("DataT")


class Response(GenericModel, Generic[DataT]):
    message: str | None
    status_code: int
    data: DataT | None
    error: List[Any] | None
