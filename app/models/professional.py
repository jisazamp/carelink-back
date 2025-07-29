from .base import Base
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey


class Profesionales(Base):
    __tablename__ = "Profesionales"

    id_profesional = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey("users.id"))
    nombres = Column(String(35), nullable=False)
    apellidos = Column(String(35), nullable=False)
    n_documento = Column(String(25), unique=True, nullable=False)
    t_profesional = Column(String(40), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    estado = Column(Enum("Activo", "Inactivo", name="estado_enum"), nullable=False)
    profesion = Column(
        Enum(
            "Médico",
            "Enfermero",
            "Nutricionista",
            "Psicólogo",
            "Fisioterapeuta",
            name="profesion_enum",
        ),
        nullable=False,
    )
    especialidad = Column(
        Enum(
            "Cardiología",
            "Pediatría",
            "Nutrición",
            "Psicología Clínica",
            "Fisioterapia",
            name="especialidad_enum",
        ),
        nullable=False,
    )
    cargo = Column(
        Enum("Jefe de Departamento", "Especialista", "Residente", name="cargo_enum"),
        nullable=False,
    )
    telefono = Column(Integer, nullable=False)
    e_mail = Column(String(30), unique=True, nullable=False)
    direccion = Column(String(50), nullable=False)
