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


class DemarcheDataBruteLastSnapshot(DemarcheDataBruteBase, Base):
    __tablename__ = "demarche_data_brute_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    # PreprocessedDossierLastSnapshot 1-N
    dossiers = relationship(
        "PreprocessedDossierLastSnapshot", back_populates="demarche_data_brute"
    )

    # VolumesPompesLastSnapshot 1-N
    volumes_pompes = relationship(
        "VolumesPompesLastSnapshot", back_populates="demarche_data_brute"
    )

    # ExtraitDeRegistreLastSnapshot 1-N
    extrait_de_registres = relationship(
        "ExtraitDeRegistreLastSnapshot", back_populates="demarche_data_brute"
    )

    # DonneesPointDePrelevementLastSnapshot 1-N
    donnees_point_de_prelevements = relationship(
        "DonneesPointDePrelevementLastSnapshot", back_populates="demarche_data_brute"
    )

    # ReleveIndexLastSnapshot 1-N
    releve_index = relationship(
        "ReleveIndexLastSnapshot", back_populates="demarche_data_brute"
    )

    # AvisLastSnapshot 1-N
    avis = relationship("AvisLastSnapshot", back_populates="demarche_data_brute")

    # MessageLastSnapshot 1-N
    message = relationship("MessageLastSnapshot", back_populates="demarche_data_brute")

    # CiterneReleveLastSnapshot 1-N
    citerne_releve = relationship(
        "CiterneReleveLastSnapshot", back_populates="demarche_data_brute"
    )

    # PrelevementReleveLastSnapshot 1-N
    prelevement_releve = relationship(
        "PrelevementReleveLastSnapshot", back_populates="demarche_data_brute"
    )


class DonneesPointDePrelevementLastSnapshot(DonneesPointDePrelevementBase, Base):
    __tablename__ = "donnees_point_de_prelevement_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    # DemarcheDataBruteLastSnapshot 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.demarche_data_brute_last_snapshot.id"
        ),
    )
    demarche_data_brute = relationship(
        "DemarcheDataBruteLastSnapshot", back_populates="donnees_point_de_prelevements"
    )

    fichiers_tableurs = relationship(
        "PieceJointeLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.fichiers_tableurs_assoc_last_snapshot",
        back_populates="tableurs",
    )
    fichiers_autres_documents = relationship(
        "PieceJointeLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.fichiers_autres_documents_assoc_last_snapshot",
        back_populates="autres_documents",
    )


class PieceJointeLastSnapshot(PieceJointeBase, Base):
    __tablename__ = "piece_jointe_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    tableurs = relationship(
        "DonneesPointDePrelevementLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.fichiers_tableurs_assoc_last_snapshot",
        back_populates="fichiers_tableurs",
    )

    autres_documents = relationship(
        "DonneesPointDePrelevementLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.fichiers_autres_documents_assoc_last_snapshot",
        back_populates="fichiers_autres_documents",
    )

    registre_papier = relationship(
        "ExtraitDeRegistreLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.extraits_de_registres_assoc_last_snapshot",
        back_populates="extraits_registres_papiers",
    )

    message = relationship(
        "MessageLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.message_assoc_last_snapshot",
        back_populates="pieces_jointes",
    )

    avis = relationship(
        "AvisLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.avis_assoc_last_snapshot",
        back_populates="pieces_jointes",
    )

    dossier = relationship(
        "PreprocessedDossierLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.dossier_fichier_tableau_suivi_camion_citerne_assoc_ls",
        back_populates="fichier_tableau_suivi_camion_citerne",
    )


class FichiersTableursAssocLastSnapshot(Base):
    __tablename__ = "fichiers_tableurs_assoc_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    donnees_point_de_prelevement_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.donnees_point_de_prelevement_last_snapshot.id"
        ),
        primary_key=True,
    )
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("demarches_simplifiees_last_snapshot.piece_jointe_last_snapshot.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )
    donnees_point_de_prelevement = relationship(
        "DonneesPointDePrelevementLastSnapshot",
    )
    piece_jointe = relationship(
        "PieceJointeLastSnapshot",
    )


class FichiersAutresDocumentsAssocLastSnapshot(Base):
    __tablename__ = "fichiers_autres_documents_assoc_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    donnees_point_de_prelevement_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.donnees_point_de_prelevement_last_snapshot.id"
        ),
        primary_key=True,
    )
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("demarches_simplifiees_last_snapshot.piece_jointe_last_snapshot.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )

    donnees_point_de_prelevement = relationship("DonneesPointDePrelevementLastSnapshot")
    piece_jointe = relationship("PieceJointeLastSnapshot")


class ExtraitsDeRegistresAssocLastSnapshot(Base):
    __tablename__ = "extraits_de_registres_assoc_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    extrait_de_registre_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.extrait_de_registre_last_snapshot.id"
        ),
        primary_key=True,
    )
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("demarches_simplifiees_last_snapshot.piece_jointe_last_snapshot.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )
    extrait_de_registre = relationship(
        "ExtraitDeRegistreLastSnapshot",
    )
    piece_jointe = relationship(
        "PieceJointeLastSnapshot",
    )


class MessageAssocLastSnapshot(Base):
    __tablename__ = "message_assoc_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("demarches_simplifiees_last_snapshot.message_last_snapshot.id"),
        primary_key=True,
    )

    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("demarches_simplifiees_last_snapshot.piece_jointe_last_snapshot.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )
    message = relationship(
        "MessageLastSnapshot",
    )
    piece_jointe = relationship(
        "PieceJointeLastSnapshot",
    )


class AvisAssocLastSnapshot(Base):
    __tablename__ = "avis_assoc_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    avis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("demarches_simplifiees_last_snapshot.avis_last_snapshot.id"),
        primary_key=True,
    )
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("demarches_simplifiees_last_snapshot.piece_jointe_last_snapshot.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )
    avis = relationship(
        "AvisLastSnapshot",
    )
    piece_jointe = relationship(
        "PieceJointeLastSnapshot",
    )


class DossierFichierTableauSuiviCamionCiterneAssocLastSnapshot(Base):
    __tablename__ = "dossier_fichier_tableau_suivi_camion_citerne_assoc_ls"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    dossier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("demarches_simplifiees_last_snapshot.dossier_last_snapshot.id"),
        primary_key=True,
    )
    piece_jointe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("demarches_simplifiees_last_snapshot.piece_jointe_last_snapshot.id"),
        primary_key=True,
        comment="La clé primaire de la piece jointe",
    )
    dossier = relationship(
        "PreprocessedDossierLastSnapshot",
    )
    piece_jointe = relationship(
        "PieceJointeLastSnapshot",
    )


class PreprocessedDossierLastSnapshot(PreprocessedDossierBase, Base):
    __tablename__ = "dossier_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    fichier_tableau_suivi_camion_citerne = relationship(
        "PieceJointeLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.dossier_fichier_tableau_suivi_camion_citerne_assoc_ls",
    )

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.demarche_data_brute_last_snapshot.id"
        ),
    )
    demarche_data_brute = relationship(
        "DemarcheDataBruteLastSnapshot", back_populates="dossiers"
    )


class ReleveIndexLastSnapshot(ReleveIndexBase, Base):
    __tablename__ = "releve_index_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.demarche_data_brute_last_snapshot.id"
        ),
    )
    demarche_data_brute = relationship(
        "DemarcheDataBruteLastSnapshot", back_populates="releve_index"
    )


class VolumesPompesLastSnapshot(VolumesPompesBase, Base):
    __tablename__ = "volumes_pompes_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.demarche_data_brute_last_snapshot.id"
        ),
    )
    demarche_data_brute = relationship(
        "DemarcheDataBruteLastSnapshot", back_populates="volumes_pompes"
    )


class ExtraitDeRegistreLastSnapshot(ExtraitDeRegistreBase, Base):
    __tablename__ = "extrait_de_registre_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.demarche_data_brute_last_snapshot.id"
        ),
    )
    demarche_data_brute = relationship(
        "DemarcheDataBruteLastSnapshot", back_populates="extrait_de_registres"
    )

    extraits_registres_papiers = relationship(
        "PieceJointeLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.extraits_de_registres_assoc_last_snapshot",
        back_populates="registre_papier",
    )


class AvisLastSnapshot(AvisBase, Base):
    __tablename__ = "avis_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    # DemarcheDataBruteLastSnapshot 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.demarche_data_brute_last_snapshot.id"
        ),
    )
    demarche_data_brute = relationship(
        "DemarcheDataBruteLastSnapshot", back_populates="avis"
    )

    pieces_jointes = relationship(
        "PieceJointeLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.avis_assoc_last_snapshot",
        back_populates="avis",
    )


class MessageLastSnapshot(MessageBase, Base):
    __tablename__ = "message_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    # DemarcheDataBruteLastSnapshot 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.demarche_data_brute_last_snapshot.id"
        ),
    )
    demarche_data_brute = relationship(
        "DemarcheDataBruteLastSnapshot", back_populates="message"
    )

    pieces_jointes = relationship(
        "PieceJointeLastSnapshot",
        secondary="demarches_simplifiees_last_snapshot.message_assoc_last_snapshot",
        back_populates="message",
    )


class CiterneReleveLastSnapshot(CiterneReleveBase, Base):
    __tablename__ = "citerne_releve_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    # DemarcheDataBruteLastSnapshot 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.demarche_data_brute_last_snapshot.id"
        ),
    )
    demarche_data_brute = relationship(
        "DemarcheDataBruteLastSnapshot", back_populates="citerne_releve"
    )


class PrelevementReleveLastSnapshot(PrelevementReleveBase, Base):
    __tablename__ = "prelevement_releve_last_snapshot"
    __table_args__ = {"schema": "demarches_simplifiees_last_snapshot"}

    # DemarcheDataBruteLastSnapshot 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "demarches_simplifiees_last_snapshot.demarche_data_brute_last_snapshot.id"
        ),
    )
    demarche_data_brute = relationship(
        "DemarcheDataBruteLastSnapshot", back_populates="prelevement_releve"
    )
