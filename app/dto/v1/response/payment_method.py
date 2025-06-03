from pydantic import BaseModel


class PaymentMethodResponseDTO(BaseModel):
    id_metodo_pago: int
    nombre: str | None

    class Config:
        orm_mode = True
