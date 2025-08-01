from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Float, DECIMAL, Text, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum


class EstadoFactura(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PAGADA = "PAGADA"
    VENCIDA = "VENCIDA"
    CANCELADA = "CANCELADA"
    ANULADA = "ANULADA"


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
    estado = Column(String(20), default="ACTIVO")
    facturas = relationship("Facturas", back_populates="contrato")

    class Config:
        orm_mode = True


class Facturas(Base):
    __tablename__ = "Facturas"

    id_factura = Column(
        Integer,
        primary_key=True,
    )
    numero_factura = Column(String(20), unique=True, nullable=True)
    id_contrato = Column(Integer, ForeignKey("Contratos.id_contrato"), nullable=True)
    id_visita_domiciliaria = Column(Integer, ForeignKey("VisitasDomiciliarias.id_visitadomiciliaria"), nullable=True)
    fecha_emision = Column(Date)
    fecha_vencimiento = Column(Date, nullable=True)
    total_factura = Column(DECIMAL(10, 2), default=0.00)
    subtotal = Column(DECIMAL(10, 2), default=0.00)
    impuestos = Column(DECIMAL(10, 2), default=0.00)
    descuentos = Column(DECIMAL(10, 2), default=0.00)
    estado_factura = Column(Enum(EstadoFactura), default=EstadoFactura.PENDIENTE)
    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    contrato = relationship("Contratos", foreign_keys=[id_contrato], lazy="joined", back_populates="facturas")
    pagos = relationship("Pagos", back_populates="factura", cascade="all, delete")
    detalles = relationship("DetalleFactura", back_populates="factura", cascade="all, delete")

    class Config:
        orm_mode = True


class DetalleFactura(Base):
    __tablename__ = "DetalleFactura"

    id_detalle_factura = Column(Integer, primary_key=True)
    id_factura = Column(Integer, ForeignKey("Facturas.id_factura"))
    id_servicio_contratado = Column(
        Integer, ForeignKey("ServiciosPorContrato.id_servicio_contratado")
    )
    cantidad = Column(Integer)
    valor_unitario = Column(DECIMAL(10, 2))
    subtotal_linea = Column(DECIMAL(10, 2), default=0.00)
    impuestos_linea = Column(DECIMAL(10, 2), default=0.00)
    descuentos_linea = Column(DECIMAL(10, 2), default=0.00)
    descripcion_servicio = Column(String(255), nullable=True)
    
    # Relaciones
    factura = relationship("Facturas", back_populates="detalles")
    servicio_contratado = relationship("ServiciosPorContrato", foreign_keys=[id_servicio_contratado])

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
    precio_por_dia = Column(DECIMAL(10, 2))
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


class Pagos(Base):
    __tablename__ = "Pagos"

    id_pago = Column(Integer, primary_key=True)
    id_factura = Column(Integer, ForeignKey("Facturas.id_factura"))
    id_metodo_pago = Column(Integer, ForeignKey("MetodoPago.id_metodo_pago"))
    id_tipo_pago = Column(Integer, ForeignKey("TipoPago.id_tipo_pago"))
    fecha_pago = Column(Date)
    valor = Column(DECIMAL(10, 2))
    factura = relationship("Facturas", back_populates="pagos")

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
