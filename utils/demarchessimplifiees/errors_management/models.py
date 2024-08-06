from sqlalchemy import Boolean, Column, Integer, String

from utils.db.base_class import Base


class ErrorMail(Base):
    __tablename__ = "error_mail"

    id_dossier = Column(Integer, index=True, comment="Identifiant unique du dossier.")
    email = Column(String, comment="Adresse email du déclarant")
    message = Column(String, comment="Message d'erreur")
    is_sent = Column(
        Boolean, default=False, comment="Indique si l'erreur a été envoyée par email"
    )
