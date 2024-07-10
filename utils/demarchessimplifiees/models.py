from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from utils.db.base_class import Base


class DemarcheDataBrute(Base):
    __tablename__ = "demarche_data_brute"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)

    hashed_collected_data = Column(
        String, unique=True, comment="Le hash du fichier de snapshot."
    )
    object_storage_key = Column(
        String, unique=True, comment="La cle du fichier de snapshot dans le bucket."
    )
    demarche_number = Column(Integer)

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


class DonneesPointDePrelevement(Base):
    __tablename__ = "donnees_point_de_prelevement"

    id_dossier = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="donnees_point_de_prelevements"
    )

    ligne = Column(
        Integer,
        comment="Ordre dans lequel l’index a été déclaré pour une même déclaration",
    )
    nom_point_prelevement = Column(String, comment="Nom du point de prélèvement")
    fichiers_tableurs = relationship(
        "PieceJointe", secondary="fichiers_tableurs_assoc", back_populates="tableurs"
    )
    fichiers_autres_documents = relationship(
        "PieceJointe",
        secondary="fichiers_autres_documents_assoc",
        back_populates="autres_documents",
    )


class PieceJointe(Base):
    __tablename__ = "piece_jointe"
    checksum = Column(String, comment="Checksum du fichier.")
    type_fichier = Column(String, comment="Le type MIME du fichier.")
    nom_fichier = Column(String, comment="Le nom du fichier.")
    demarches_simplifiees_url = Column(
        String, comment="l'URL sur demarches simplifiees"
    )
    object_storage_key = Column(String, comment="La cle du fichier dans le bucket.")

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


class PreprocessedDossier(Base):
    __tablename__ = "dossier"
    id_dossier = Column(Integer, index=True, comment="Identifiant unique du dossier.")
    adresse_email_connexion = Column(
        String,
        comment="Email de connexion associé au compte Démarches simplifiées du déclarant",
    )
    civilite_declarant = Column(String, comment="Civilité du déclarant")
    nom_declarant = Column(String, comment="Nom du déclarant")
    prenom_declarant = Column(String, comment="Prénom du déclarant")
    depot_pour_mandataire = Column(
        Boolean, comment="Indique si le déclarant dépose pour un mantataire"
    )
    nom_mandataire = Column(String, nullable=True, comment="Nom du mandataire")
    prenom_mandataire = Column(String, nullable=True, comment="Prénom du mandataire")
    archive = Column(Boolean, comment="Indique si le dossier est archivé")
    etat_dossier = Column(String, comment="Etat d’avancement du dossier")
    derniere_mise_a_jour = Column(
        DateTime,
        comment="Date de dernière mise à jour du dossier (notamment les avis, la messagerie…)",
    )
    date_depot = Column(DateTime, comment="Date de dépôt du dossier")
    date_passage_instruction = Column(
        DateTime, comment="Date de passage en instruction"
    )
    date_traitement = Column(DateTime, comment="Date de traitement par l’instructeur")
    motivation_decision = Column(
        String, comment="Motivation de la décision par l’instructeur"
    )
    instructeurs = Column(String, comment="Instructeurs affectés à la démarche")
    groupe_instructeur = Column(
        String, comment="Groupe d’instructeurs affecté à la démarche"
    )

    coordonnees = Column(String)
    adresse_email_declarant = Column(String, comment="Adresse email du déclarant")
    numero_telephone_declarant = Column(
        String, comment="Numéro de téléphone du déclarant"
    )
    statut_declarant = Column(
        String,
        comment="Statut du déclarant (particulier ou représentant d’une structure)",
    )
    raison_sociale_structure = Column(String, comment="Raison sociale de la structure")
    type_prelevement = Column(String, comment="Type de prélèvement")
    point_prelevement_eau = Column(String)
    numero_arrete_aot = Column(String, comment="Numéro de l’arrêté préfectoral d’AOT")
    prelevement_citerne = Column(String)
    volume_preleve = Column(String)
    mode_transmission_donnees_camion_citerne = Column(
        String,
        comment="Mode de transmission des données pour les AOT camion citerne (une à une, ou au format tableur)",
    )
    volumes_pompes_jour = Column(String)
    copie_registre_papier = Column(String)
    conclusion = Column(String)
    commentaire = Column(
        String, comment="Commentaire libre du déclarant sur la déclaration"
    )
    volumes_annuels_pompes = Column(String)
    transmission_extrait_numerique_registre = Column(String)
    declaration_point_prelevement = Column(String)
    date_activation_point_prelevement = Column(String)
    type_autre_prelevement = Column(String)
    releve_index_compteur = Column(String)
    informations_compteur = Column(String)
    numero_serie_compteur = Column(
        String, comment="Numéro de série du compteur (pour les AOT agricoles)"
    )
    prelevement_icpe = Column(String)
    donnees_standardisees = Column(String)
    prelevement_aep_zre = Column(String)
    nom_point_prelevement = Column(String)
    validation_informations = Column(
        Boolean,
        comment="Déclaration par le préleveur que les informations sont exactes",
    )
    details_prelevements_camion_citerne = Column(Boolean)
    donnees_compteur_volumetrique = Column(
        Boolean,
        comment="Indique sur les données sont issues d’un compteur volumétrique (pour les AOT agricoles)",
    )
    compteur_lecture_directe = Column(
        Boolean,
        comment="Indique s’il s’agit d’un compteur à lecture directe (pour les AOT agricoles)",
    )
    panne_compteur = Column(
        Boolean,
        comment="Indique si une panne ou un changement de compteur est déclarée (pour les AOT agricoles)",
    )
    prelevement_sur_periode_aot_agricole = Column(Boolean)
    prelevement_sur_periode_camion_citerne = Column(
        Boolean,
        comment="Pour les AOT de camions citernes, indique si des prélèvements ont été réalisés sur la période concernée par la déclaration (mois précédent)",
    )
    date_debut_periode_declaree = Column(
        DateTime, comment="Date du début de la période concernée par la déclaration"
    )
    date_fin_periode_declaree = Column(
        DateTime, comment="Date de fin de la période concernée par la déclaration"
    )
    annee_prelevement_camion_citerne = Column(
        Integer,
        comment="Pour les camions citernes, année de prélèvement (permet de définir le niveau de précision attendu dans la déclaration)",
    )

    prelevement_points_autorises_aot_2023 = Column(
        Boolean,
        comment="Avez-vous prélevé sur au moins un des points autorisés par votre AOT durant l'année 2023 ?",
    )
    rappel_obligation_mensuelle_declaration = Column(
        Boolean,
        comment="Souhaiteriez-vous recevoir le 1er de chaque mois un mail vous rappelant l'obligation mensuelle de déclaration ?",
    )
    acceptation_contact_deal = Column(
        Boolean,
        comment="Accepteriez-vous d’être recontacté.e par la DEAL pour échanger davantage sur le sujet ?",
    )

    mois_prelevement_camion_citerne = Column(
        String,
        comment="En quel mois les prélèvements que vous allez déclarer ont-ils été réalisés ?",
    )
    note_facilite_utilisation = Column(
        String,
        comment="Donnez une note sur la facilité de prise en main de l’outil démarches simplifiées",
    )
    remarque_note = Column(
        String, comment="Souhaitez-vous apporter une remarque à cette note ?"
    )
    temps_remplissage_questionnaire = Column(
        String, comment="Combien de temps avez-vous passé à remplir ce questionnaire ?"
    )
    amelioration_temps_remplissage = Column(
        String,
        comment="Avez-vous une idée ce que qui pourrait être amélioré pour réduire ce temps ?",
    )
    temps_formatage_donnees = Column(
        String,
        comment="Combien de temps avez-vous passé au formatage des données (utilisation du modèle de tableur imposé) ?",
    )
    televersement_tableur_brutes = Column(
        String,
        comment="Qui est la personne qui a téléversé le tableur de données brutes dans l’outil Démarches Simplifiées ?",
    )
    acces_formulaire = Column(
        String, comment="Comment cette personne a-t-elle eu accès au formulaire ?"
    )
    declarant_demarche_simplifiee = Column(
        String,
        comment="Qui est la personne qui a fait la déclaration sur Démarches Simplifiées ?",
    )
    raison_non_declaration_preleveur = Column(
        String,
        comment="Pour quelles raisons la personne en charge du prélèvement n'a-t-elle pas pu faire la déclaration elle-même ?",
    )
    demande_documentation = Column(
        String,
        comment="Souhaiteriez-vous disposer d’une documentation sur le remplissage de ce formulaire et la façon de remplir le modèle de tableau de données ?",
    )
    amelioration_documentation = Column(
        String,
        comment="Sous quelle forme une documentation d’utilisation vous semble la plus utile ?",
    )
    suggestion_informations_visualisation = Column(
        String,
        comment="Si vous le souhaitez, vous pouvez nous faire part des informations que vous aimeriez voir figurer dans cet outil de visualisation de données, "
        + "et qui pourraient vous être utiles pour mieux suivre vos prélèvements au fil du temps.",
    )

    fichier_tableau_suivi_camion_citerne = relationship(
        "PieceJointe", secondary="dossier_fichier_tableau_suivi_camion_citerne_assoc"
    )

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="dossiers")


class ReleveIndex(Base):
    __tablename__ = "releve_index"
    ligne = Column(
        Integer,
        comment="Ordre dans lequel l’index a été déclaré pour une même déclaration",
    )
    date_releve_index = Column(DateTime)
    releve_index = Column(Float)

    id_dossier = Column(Integer)

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="releve_index"
    )


class VolumesPompes(Base):
    __tablename__ = "volumes_pompes"

    id_dossier = Column(Integer, comment="Identifiant unique du dossier")

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="volumes_pompes"
    )

    ligne = Column(
        Integer,
        comment="Ordre dans lequel l’index a été déclaré pour une même déclaration",
    )
    point_prelevement_camion_citerne = Column(
        String, comment="Point de prélèvement pour le camion citerne"
    )
    annee_prelevement_camion_citerne_2 = Column(
        Integer,
        comment="Année à laquelle le volume prélevé est associé (pour les prélèvements antérieurs à 2024, on accepte un chiffre globalisé à l’année)",
    )
    volumes_pompes_camions_citernes = Column(
        Float,
        comment="Volumes pompés par les camions citernes (en m³), pour les déclarants ayant voulu déclarer leurs données une à une",
    )
    date_prelevement_camion_citerne = Column(
        DateTime, comment="Date précise de prélèvement par camion citerne"
    )


class ExtraitDeRegistre(Base):
    __tablename__ = "extrait_de_registre"

    id_dossier = Column(Integer, comment="Identifiant unique du dossier")

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="extrait_de_registres"
    )

    ligne = Column(
        Integer,
        comment="Ordre dans lequel l’index a été déclaré pour une même déclaration",
    )
    extraits_registres_papiers = relationship(
        "PieceJointe",
        secondary="extraits_de_registres_assoc",
        back_populates="registre_papier",
    )


class Avis(Base):
    __tablename__ = "avis"
    id_dossier = Column(Integer, comment="Identifiant unique du dossier")
    id_avis = Column(String, comment="Identifiant unique de l'avis")

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="avis")

    question = Column(String, comment="Question de l’instructeur")
    reponse = Column(String, comment="Réponse de l’expert")
    date_question = Column(DateTime, comment="Date de la question")
    date_reponse = Column(DateTime, comment="Date de la reponse")
    claimant_email = Column(String, comment="Email du claimant")
    expert_email = Column(String, comment="Email de l'expert")
    pieces_jointes = relationship(
        "PieceJointe", secondary="avis_assoc", back_populates="avis"
    )


class Message(Base):
    __tablename__ = "message"

    id_dossier = Column(Integer, comment="Identifiant unique du dossier")
    id_message = Column(
        String, comment="Identifiant unique du messge dans demarches simplifiees"
    )

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship("DemarcheDataBrute", back_populates="message")

    email = Column(String, comment="Email contacté")
    body = Column(String, comment="Corps du message")
    date_creation = Column(DateTime, comment="Date de reception du message")
    pieces_jointes = relationship(
        "PieceJointe", secondary="message_assoc", back_populates="message"
    )


class CiterneReleve(Base):
    __tablename__ = "citerne_releve"
    id_dossier = Column(Integer, comment="Identifiant unique du dossier")

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="citerne_releve"
    )

    date_releve = Column(DateTime, comment="Date du relevé")
    point_prelevement = Column(String, comment="Point de prélèvement")
    volume = Column(Float, comment="Volume prélevé")


class PrelevementReleve(Base):
    __tablename__ = "prelevement_releve"

    id_dossier = Column(Integer, comment="Identifiant unique du dossier")

    # DemarcheDataBrute 1-N
    demarche_data_brute_id = Column(
        UUID(as_uuid=True), ForeignKey("demarche_data_brute.id")
    )
    demarche_data_brute = relationship(
        "DemarcheDataBrute", back_populates="prelevement_releve"
    )

    date = Column(DateTime, comment="Date du relevé")
    heure = Column(DateTime, comment="Heure du relevé")
    valeur = Column(Float, comment="Valeur du relevé")
    nom_parametre = Column(String, comment="Nom du paramètre")
    type = Column(String, comment="Type de relevé")
    frequence = Column(String, comment="Fréquence de relevé")
    unite = Column(String, comment="Unité de relevé")
    detail_point_suivi = Column(String, comment="Détail du point de suivi")
    profondeur = Column(Float, comment="Profondeur du point de suivi")
    date_debut = Column(DateTime, comment="Date de début de relevé")
    date_fin = Column(DateTime, comment="Date de fin de relevé")
    remarque = Column(String, comment="Remarque sur le relevé")
    nom_point_prelevement = Column(String, comment="Nom du point de prélèvement")
    nom_point_de_prelevement_associe = Column(
        String, comment="Nom du point de prélèvement associé"
    )
    remarque_fonctionnement_point_de_prelevement = Column(
        String, comment="Remarque sur le fonctionnement du point de prélèvement"
    )
