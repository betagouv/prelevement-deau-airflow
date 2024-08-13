from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects import postgresql

from utils.db.base_class import Base


class ErrorMail(Base):
    __tablename__ = "error_mail"

    id_dossier = Column(Integer, index=True, comment="Identifiant unique du dossier.")
    email = Column(String, comment="Adresse email du déclarant")
    message = Column(String, comment="Message d'erreur")
    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        postgresql.UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
