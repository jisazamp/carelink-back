from datetime import date
from pydantic import BaseModel


class PaymentMethodResponseDTO(BaseModel):
    id_metodo_pago: int
    nombre: str | None

    class Config:
        orm_mode = True


class PaymentResponseDTO(BaseModel):
    id_pago: int
    id_factura: int
    id_metodo_pago: int
    id_tipo_pago: int
    fecha_pago: date
    valor: float

    class Config:
        orm_mode = True
