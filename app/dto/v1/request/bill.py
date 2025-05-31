from pydantic import BaseModel


class CalculatePartialBillRequestDTO(BaseModel):
    service_ids: list[int]
    quantities: list[int]
    year: int
