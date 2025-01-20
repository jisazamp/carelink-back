from .base import Base
from .family_member import FamilyMember
from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship


class FamiliaresYAcudientesPorUsuario(Base):
    __tablename__ = "familiares_y_acudientes_por_usuario"

    id_acudiente = Column(
        Integer,
        ForeignKey("Familiares.id_acudiente", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    id_usuario = Column(
        Integer,
        ForeignKey("Usuarios.id_usuario", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    parentesco = Column(
        Enum(
            "Amigo",
            "Hermana",
            "Hermano",
            "Madre",
            "Otro",
            "Padre",
            "Prima",
            "Primo",
            "Tía",
            "Tío",
            name="parentesco_enum",
        ),
        nullable=False,
    )
    acudiente = relationship(FamilyMember, foreign_keys=[id_acudiente])
