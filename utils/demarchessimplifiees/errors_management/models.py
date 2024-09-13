from sqlalchemy import Column, Integer, String

from utils.db.base_class import Base


class ErrorMail(Base):
    __tablename__ = "error_mail"
    __table_args__ = {"schema": "prelevement_deau"}

    id_dossier = Column(Integer, index=True, comment="Identifiant unique du dossier.")
    email = Column(String, comment="Adresse email du déclarant")
    message = Column(String, comment="Message d'erreur")
