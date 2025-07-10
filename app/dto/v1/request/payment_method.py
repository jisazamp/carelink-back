from pydantic import BaseModel, validator
from datetime import date
from decimal import Decimal


class CreateUserPaymentRequestDTO(BaseModel):
    id_factura: int
    id_metodo_pago: int
    id_tipo_pago: int
    fecha_pago: date
    valor: Decimal

    @validator('valor')
    def validate_valor(cls, v):
        if v <= 0:
            raise ValueError('El valor del pago debe ser mayor a 0')
        return v

    @validator('id_factura')
    def validate_id_factura(cls, v):
        if v <= 0:
            raise ValueError('El ID de factura debe ser válido')
        return v

    @validator('id_metodo_pago')
    def validate_id_metodo_pago(cls, v):
        if v <= 0:
            raise ValueError('El método de pago debe ser válido')
        return v

    @validator('id_tipo_pago')
    def validate_id_tipo_pago(cls, v):
        if v <= 0:
            raise ValueError('El tipo de pago debe ser válido')
        return v
