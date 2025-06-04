from pydantic import BaseModel
from datetime import date


class CreateUserPaymentRequestDTO(BaseModel):
    id_factura: int
    id_metodo_pago: int
    fecha_pago: date
    valor: float
