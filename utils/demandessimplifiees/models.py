from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from utils.db.base_class import Base


class DemarcheDataBrute(Base):
    __tablename__ = "demarche_data_brute"
    hashed_collected_data = Column(String, unique=True)
    file_path = Column(String, unique=True)
    demarche_number = Column(Integer)

    # PreprocessedDossier 1-N
    preprocessed_dossiers = relationship("PreprocessedDossier", back_populates="demarche_data_brute")

    # VolumesPompes 1-N
    volumes_pompes = relationship("VolumesPompes", back_populates="demarche_data_brute")

    # ExtraitDeRegistre 1-N
    extrait_de_registres = relationship("ExtraitDeRegistre", back_populates="demarche_data_brute")

    # DonneesPointDePrelevement 1-N
    donnees_point_de_prelevements = relationship("DonneesPointDePrelevement", back_populates="demarche_data_brute")

    # ReleveIndex 1-N
    releve_index = relationship("ReleveIndex", back_populates="demarche_data_brute")


class PreprocessedDossier(Base):
    __tablename__ = "preprocessed_dossier"
    number = Column(Integer, index=True)
    email = Column(String)
    civilite = Column(String)
    nom = Column(String)
    prenom = Column(String)
    deposeParUnTiers = Column(Boolean)
    nomMandataire = Column(String, nullable=True)
    prenomMandataire = Column(String, nullable=True)
    archived = Column(Boolean)
    state = Column(String)
    dateDerniereModification = Column(DateTime)
    dateDepot = Column(DateTime)
    datePassageEnInstruction = Column(DateTime)
    dateTraitement = Column(DateTime)
    motivation = Column(String)
    instructeurs = Column(String)
    groupe_instructeur = Column(String)
    coordonnees = Column(String)
    adresse_email = Column(String)
    numero_telephone = Column(String)
    statut_declarant = Column(String)
    raison_sociale_structure = Column(String)
    point_prelevement_eau = Column(String)
    type_prelevement = Column(String)
    numero_arrete_aot = Column(String)
    prelevement_citerne = Column(String)
    volume_preleve = Column(String)
    mode_transmission_donnees = Column(String)
    volumes_pompes_jour = Column(String)
    copie_registre_papier = Column(String)
    conclusion = Column(String)
    commentaire = Column(String)
    volumes_annuels_pompes = Column(String)
    transmission_extrait_numerique_registre = Column(String)
    declaration_point_prelevement = Column(String)
    date_activation_point_prelevement = Column(String)
    type_autre_prelevement = Column(String)
    releve_index_compteur = Column(String)
    informations_compteur = Column(String)
    numero_serie_compteur = Column(String)
    prelevement_icpe = Column(String)
    donnees_standardisees = Column(String)
    prelevement_aep_zre = Column(String)

    validation_informations = Column(Boolean)
    details_prelevements = Column(Boolean)
    donnees_compteur_volumetrique = Column(Boolean)
    compteur_lecture_directe = Column(Boolean)
    signalement_panne_compteur = Column(Boolean)
    prelevement_autorise_mois_precedent = Column(Boolean)
    au_moins_un_prelevement = Column(Boolean)

    date_debut_declaration = Column(DateTime)
    date_fin_declaration = Column(DateTime)

    annee_prelevement = Column(Integer)
    nom_point_prelevement = Column(String)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="preprocessed_dossiers")

class ReleveIndex(Base):
    __tablename__ = "releve_index"
    ligne = Column(Integer)
    date = Column(DateTime)
    index = Column(Float)

    dossier_id = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="releve_index")


class VolumesPompes(Base):
    __tablename__ = "volumes_pompes"

    dossier_id = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="volumes_pompes")

    ligne = Column(Integer)
    point_prelevement = Column(String)
    annee = Column(Integer)
    volume_pompe = Column(Float)
    date = Column(DateTime)


class ExtraitDeRegistre(Base):
    __tablename__ = "extrait_de_registre"

    dossier_id = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="extrait_de_registres")

    ligne = Column(Integer)
    extrait_registre = Column(String)


class DonneesPointDePrelevement(Base):
    __tablename__ = "donnees_point_de_prelevement"
    dossier_id = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="donnees_point_de_prelevements")

    ligne = Column(Integer)
    point_prelevement = Column(String)
    donnees_standardisees = Column(String)
    autres_documents = Column(String)
