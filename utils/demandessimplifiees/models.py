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
    dossiers = relationship("PreprocessedDossier", back_populates="demarche_data_brute")

    # VolumesPompes 1-N
    volumes_pompes = relationship("VolumesPompes", back_populates="demarche_data_brute")

    # ExtraitDeRegistre 1-N
    extrait_de_registres = relationship("ExtraitDeRegistre", back_populates="demarche_data_brute")

    # DonneesPointDePrelevement 1-N
    donnees_point_de_prelevements = relationship("DonneesPointDePrelevement", back_populates="demarche_data_brute")

    # ReleveIndex 1-N
    releve_index = relationship("ReleveIndex", back_populates="demarche_data_brute")

    # Avis 1-N
    avis = relationship("Avis", back_populates="demarche_data_brute")

    # Message 1-N
    message = relationship("Message", back_populates="demarche_data_brute")


class PreprocessedDossier(Base):
    __tablename__ = "dossier"
    id_dossier = Column(Integer, index=True)
    adresse_email_connexion = Column(String)
    civilite_declarant = Column(String)
    nom_declarant = Column(String)
    prenom_declarant = Column(String)
    depot_pour_mandataire = Column(Boolean)
    nom_mandataire = Column(String, nullable=True)
    prenom_mandataire = Column(String, nullable=True)
    archive = Column(Boolean)
    etat_dossier = Column(String)
    derniere_mise_a_jour = Column(DateTime)
    date_depot = Column(DateTime)
    date_passage_instruction = Column(DateTime)
    date_traitement = Column(DateTime)
    motivation_decision = Column(String)
    instructeurs = Column(String)
    groupe_instructeur = Column(String)

    coordonnees = Column(String)
    adresse_email_declarant = Column(String)
    numero_telephone = Column(String)
    statut_declarant = Column(String)
    raison_sociale_structure = Column(String)
    type_prelevement = Column(String)
    point_prelevement_eau = Column(String)
    numero_arrete_aot = Column(String)
    prelevement_citerne = Column(String)
    volume_preleve = Column(String)
    mode_transmission_donnees_camion_citerne = Column(String)
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
    nom_point_prelevement = Column(String)

    validation_informations = Column(Boolean)
    details_prelevements_camion_citerne = Column(Boolean)
    donnees_compteur_volumetrique = Column(Boolean)
    compteur_lecture_directe = Column(Boolean)
    panne_compteur = Column(Boolean)
    prelevement_sur_periode_aot_agricole = Column(Boolean)
    prelevement_sur_periode_camion_citerne = Column(Boolean)

    date_debut_periode_declaree = Column(DateTime)
    date_fin_periode_declaree = Column(DateTime)

    annee_prelevement_camion_citerne = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="dossiers")


class ReleveIndex(Base):
    __tablename__ = "releve_index"
    ligne = Column(Integer)
    date_releve_index = Column(DateTime)
    releve_index = Column(Float)

    id_dossier = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="releve_index")


class VolumesPompes(Base):
    __tablename__ = "volumes_pompes"

    id_dossier = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="volumes_pompes")

    ligne = Column(Integer)
    point_prelevement_camion_citerne = Column(String)
    annee_prelevement_camion_citerne_2 = Column(Integer)
    volumes_pompes_camions_citernes = Column(Float)
    date_prelevement_camion_citerne = Column(DateTime)


class ExtraitDeRegistre(Base):
    __tablename__ = "extrait_de_registre"

    id_dossier = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="extrait_de_registres")

    ligne = Column(Integer)
    extrait_registre_papier = Column(String)


class DonneesPointDePrelevement(Base):
    __tablename__ = "donnees_point_de_prelevement"
    id_dossier = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="donnees_point_de_prelevements")

    ligne = Column(Integer)
    nom_point_prelevement = Column(String)
    fichier_tableur = Column(String)
    fichier_autre_document = Column(String)


class Avis(Base):
    __tablename__ = "avis"
    id_dossier = Column(Integer)
    id_avis = Column(String)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="avis")

    question = Column(String)
    reponse = Column(String)
    date_question = Column(DateTime)
    date_reponse = Column(DateTime)
    claimant_email = Column(String)
    expert_email = Column(String)
    pieces_jointes = Column(String)


class Message(Base):
    __tablename__ = "message"

    id_dossier = Column(Integer)
    id_message = Column(String)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(UUID(as_uuid=True), ForeignKey("demarche_data_brute.id"))
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="message")

    email = Column(String)
    body = Column(String)
    date_creation = Column(DateTime)
    pieces_jointes = Column(String)
