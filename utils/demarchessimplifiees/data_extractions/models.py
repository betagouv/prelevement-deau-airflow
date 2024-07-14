from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from utils.db.base_class import Base
from utils.demarchessimplifiees.models import (
    AvisBase,
    CiterneReleveBase,
    DemarcheDataBruteBase,
    DonneesPointDePrelevementBase,
    ExtraitDeRegistreBase,
    MessageBase,
    PieceJointeBase,
    PrelevementReleveBase,
    PreprocessedDossierBase,
    ReleveIndexBase,
    VolumesPompesBase,
)


class DemarcheDataBrute(DemarcheDataBruteBase, Base):
    __tablename__ = "demarche_data_brute"

    # PreprocessedDossier 1-N
    dossiers = relationship("PreprocessedDossier", back_populates="demarche_data_brute")

    # VolumesPompes 1-N
    volumes_pompes = relationship("VolumesPompes", back_populates="demarche_data_brute")

    # ExtraitDeRegistre 1-N
    extrait_de_registres = relationship(
        "ExtraitDeRegistre", back_populates="demarche_data_brute"
    )

    # DonneesPointDePrelevement 1-N
    donnees_point_de_prelevements = relationship(
        "DonneesPointDePrelevement", back_populates="demarche_data_brute"
    )

    # ReleveIndex 1-N
    releve_index = relationship("ReleveIndex", back_populates="demarche_data_brute")

    # Avis 1-N
    avis = relationship("Avis", back_populates="demarche_data_brute")

    # Message 1-N
    message = relationship("Message", back_populates="demarche_data_brute")

    # CiterneReleve 1-N
    citerne_releve = relationship("CiterneReleve", back_populates="demarche_data_brute")

    # PrelevementReleve 1-N
    prelevement_releve = relationship(
        "PrelevementReleve", back_populates="demarche_data_brute"
    )


class DonneesPointDePrelevement(DonneesPointDePrelevementBase, Base):
    __tablename__ = "donnees_point_de_prelevement"

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="donnees_point_de_prelevements"
    )

    fichiers_tableurs = relationship(
        "PieceJointe", secondary="fichiers_tableurs_assoc", back_populates="tableurs"
    )
    fichiers_autres_documents = relationship(
        "PieceJointe",
        secondary="fichiers_autres_documents_assoc",
        back_populates="autres_documents",
    )


class PieceJointe(PieceJointeBase, Base):
    __tablename__ = "piece_jointe"
    tableurs = relationship(
        "DonneesPointDePrelevement",
        secondary="fichiers_tableurs_assoc",
        back_populates="fichiers_tableurs",
    )
    autres_documents = relationship(
        "DonneesPointDePrelevement",
        secondary="fichiers_autres_documents_assoc",
        back_populates="fichiers_autres_documents",
    )

    registre_papier = relationship(
        "ExtraitDeRegistre",
        secondary="extraits_de_registres_assoc",
        back_populates="extraits_registres_papiers",
    )
    message = relationship(
        "Message", secondary="message_assoc", back_populates="pieces_jointes"
    )
    avis = relationship("Avis", secondary="avis_assoc", back_populates="pieces_jointes")

    dossier = relationship(
        "PreprocessedDossier",
        secondary="dossier_fichier_tableau_suivi_camion_citerne_assoc",
        back_populates="fichier_tableau_suivi_camion_citerne",
    )


class FichiersTableursAssoc(Base):
    __tablename__ = "fichiers_tableurs_assoc"
    donnees_point_de_prelevement_id = Column(
        UUID(as_uuid=True),
        ForeignKey("donnees_point_de_prelevement.id"),
        primary_key=True,
    )
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("piece_jointe.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )


class FichiersAutresDocumentsAssoc(Base):
    __tablename__ = "fichiers_autres_documents_assoc"
    donnees_point_de_prelevement_id = Column(
        UUID(as_uuid=True),
        ForeignKey("donnees_point_de_prelevement.id"),
        primary_key=True,
    )
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("piece_jointe.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )


class ExtraitsDeRegistresAssoc(Base):
    __tablename__ = "extraits_de_registres_assoc"
    extrait_de_registre_id = Column(
        UUID(as_uuid=True), ForeignKey("extrait_de_registre.id"), primary_key=True
    )
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("piece_jointe.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )


class MessageAssoc(Base):
    __tablename__ = "message_assoc"
    message_id = Column(UUID(as_uuid=True), ForeignKey("message.id"), primary_key=True)
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("piece_jointe.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )


class AvisAssoc(Base):
    __tablename__ = "avis_assoc"
    avis_id = Column(UUID(as_uuid=True), ForeignKey("avis.id"), primary_key=True)
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("piece_jointe.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )


class DossierFichierTableauSuiviCamionCiterneAssoc(Base):
    __tablename__ = "dossier_fichier_tableau_suivi_camion_citerne_assoc"
    dossier_id = Column(UUID(as_uuid=True), ForeignKey("dossier.id"), primary_key=True)
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("piece_jointe.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )


class PreprocessedDossier(PreprocessedDossierBase, Base):
    __tablename__ = "dossier"

    fichier_tableau_suivi_camion_citerne = relationship(
        "PieceJointe", secondary="dossier_fichier_tableau_suivi_camion_citerne_assoc"
    )

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="dossiers")


class ReleveIndex(ReleveIndexBase, Base):
    __tablename__ = "releve_index"

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="releve_index"
    )


class VolumesPompes(VolumesPompesBase, Base):
    __tablename__ = "volumes_pompes"

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="volumes_pompes"
    )


class ExtraitDeRegistre(ExtraitDeRegistreBase, Base):
    __tablename__ = "extrait_de_registre"

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="extrait_de_registres"
    )

    extraits_registres_papiers = relationship(
        "PieceJointe",
        secondary="extraits_de_registres_assoc",
        back_populates="registre_papier",
    )


class Avis(AvisBase, Base):
    __tablename__ = "avis"

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="avis")

    pieces_jointes = relationship(
        "PieceJointe", secondary="avis_assoc", back_populates="avis"
    )


class Message(MessageBase, Base):
    __tablename__ = "message"

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="message")

    pieces_jointes = relationship(
        "PieceJointe", secondary="message_assoc", back_populates="message"
    )


class CiterneReleve(CiterneReleveBase, Base):
    __tablename__ = "citerne_releve"

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="citerne_releve"
    )


class PrelevementReleve(PrelevementReleveBase, Base):
    __tablename__ = "prelevement_releve"

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="prelevement_releve"
    )
