from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Float
from sqlalchemy.orm import relationship


class Contratos(Base):
    __tablename__ = "Contratos"

    id_contrato = Column(
        Integer,
        primary_key=True,
    )
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=True)
    tipo_contrato = Column(String)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    facturar_contrato = Column(Boolean)
    usuario = relationship("Usuarios", foreign_keys=[id_usuario], lazy="joined")

    class Config:
        orm_mode = True


class Facturas(Base):
    __tablename__ = "Facturas"

    id_factura = Column(
        Integer,
        primary_key=True,
    )
    id_contrato = Column(Integer, ForeignKey("Contratos.id_contrato"), nullable=True)
    fecha_emision = Column(Date)
    total_factura = Column(Float)
    contrato = relationship("Contratos", foreign_keys=[id_contrato], lazy="joined")

    class Config:
        orm_mode = True


class DetalleFactura(Base):
    __tablename__ = "DetalleFactura"

    id_detalle_factura = Column(Integer, primary_key=True)
    id_factura = Column(Integer, ForeignKey("Facturas.id_factura"))
    id_servicio_contratado = Column(
        Integer, ForeignKey("ServiciosPorcontrato.id_servicio_contratado")
    )
    cantidad = Column(Integer)
    valor_unitario = Column(Float)

    class Config:
        orm_mode = True


class Servicios(Base):
    __tablename__ = "Servicios"

    id_servicio = Column(
        Integer,
        primary_key=True,
    )
    nombre = Column(String)
    descripcion = Column(String)

    class Config:
        orm_mode = True


class ServiciosPorContrato(Base):
    __tablename__ = "ServiciosPorContrato"

    id_servicio_contratado = Column(
        Integer,
        primary_key=True,
    )
    id_contrato = Column(Integer, ForeignKey("Contratos.id_contrato"))
    id_servicio = Column(Integer, ForeignKey("Servicios.id_servicio"))
    fecha = Column(Date)
    descripcion = Column(String)
    precio_por_dia = Column(Float)
    contrato = relationship("Contratos", foreign_keys=[id_contrato], lazy="joined")
    servicio = relationship("Servicios", foreign_keys=[id_servicio], lazy="joined")

    class Config:
        orm_mode = True


class FechasServicio(Base):
    __tablename__ = "FechasServicio"

    id_fecha_servicio = Column(Integer, primary_key=True)
    id_servicio_contratado = Column(
        Integer, ForeignKey("ServiciosPorContrato.id_servicio_contratado")
    )
    fecha = Column(Date)

    class Config:
        orm_mode = True


class TipoActividad(Base):
    __tablename__ = "TipoActividad"

    id = Column(
        Integer,
        primary_key=True,
    )
    tipo = Column(String(50))

    class Config:
        orm_mode = True


class Pagos(Base):
    __tablename__ = "Pagos"

    id_pago = Column(Integer, primary_key=True)
    id_factura = Column(Integer, ForeignKey("Facturas.id_factura"))
    id_metodo_pago = Column(Integer, ForeignKey("MetodoPago.id_metodo_pago"))
    id_tipo_pago = Column(Integer, ForeignKey("TipoPago.id_tipo_pago"))
    fecha_pago = Column(Date)
    valor = Column(Float)

    class Config:
        orm_mode = True


class MetodoPago(Base):
    __tablename__ = "MetodoPago"

    id_metodo_pago = Column(Integer, primary_key=True)
    nombre = Column(String)

    class Config:
        orm_mode = True


class TipoPago(Base):
    __tablename__ = "TipoPago"

    id_tipo_pago = Column(Integer, primary_key=True)
    nombre = Column(String)

    class Config:
        orm_mode = True
