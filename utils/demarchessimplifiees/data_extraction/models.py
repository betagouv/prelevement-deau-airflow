from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from utils.db.base_class import Base
from utils.demarchessimplifiees.data_extraction.schemas import (
    Civilite,
    DossierEtatEnum,
    DossierSousEtatEnum,
    TypePrelevementEnum,
    TypeTransmissionDonneesEnum,
)


class Dossier(Base):
    __tablename__ = "dossier"

    # ID
    id = Column(Integer, primary_key=True, comment="Identifiant unique du dossier.")
    # Archivé
    archive = Column(Boolean, comment="Indique si le dossier est archivé")
    # État du dossier
    etat_dossier = Column(
        Enum(DossierEtatEnum, name="dossieretatenum"),
        comment="Etat d’avancement du dossier",
    )
    # Sous-état du dossier
    sous_etat_dossier = Column(
        Enum(DossierSousEtatEnum, name="dossiersousetatenum"),
        comment="Sous-état d’avancement du dossier",
    )
    # Dernière mise à jour le
    derniere_mise_a_jour = Column(
        DateTime,
        comment="Date de dernière mise à jour du dossier (notamment les avis, la messagerie…)",
    )
    # Déposé le
    date_depot = Column(DateTime, comment="Date de dépôt du dossier")
    # Passé en instruction le
    date_passage_instruction = Column(
        DateTime, comment="Date de passage en instruction"
    )
    # Date de la dernière correction en attente
    date_derniere_correction_en_attente = Column(
        DateTime, comment="Date de la dernière correction en attente"
    )
    # Traité le
    date_traitement = Column(DateTime, comment="Date de traitement par l’instructeur")
    # Motivation de la décision
    motivation_decision = Column(
        String, comment="Motivation de la décision par l’instructeur"
    )
    # Instructeurs
    instructeurs = Column(String, comment="Instructeurs affectés à la démarche")
    # Groupe instructeur
    groupe_instructeur = Column(
        String, comment="Groupe d’instructeurs affecté à la démarche"
    )

    # Identité du demandeur
    # Email
    adresse_email_connexion = Column(
        String,
        comment="Email de connexion associé au compte Démarches simplifiées du déclarant",
    )
    # Civilité
    civilite_declarant = Column(
        Enum(Civilite, name="civilite"), comment="Civilité du déclarant"
    )
    # Nom
    nom_declarant = Column(String, comment="Nom du déclarant")
    # Prénom
    prenom_declarant = Column(String, comment="Prénom du déclarant")
    # Nom du mandataire
    nom_mandataire = Column(String, nullable=True, comment="Nom du mandataire")
    # Prénom du mandataire
    prenom_mandataire = Column(String, nullable=True, comment="Prénom du mandataire")
    # Dépôt pour un tiers
    depot_pour_mandataire = Column(
        Boolean, comment="Indique si le déclarant dépose pour un mantataire"
    )

    # Vos coordonnées
    # Adresse électronique :
    adresse_email_declarant = Column(String, comment="Adresse email du déclarant")
    # Numéro de téléphone :
    numero_telephone_declarant = Column(
        String, comment="Numéro de téléphone du déclarant"
    )
    # Vous formulez cette déclaration en tant que :
    statut_declarant = Column(
        String,
        comment="Statut du déclarant (particulier ou représentant d’une structure)",
    )
    # Raison sociale de votre structure :
    raison_sociale_structure = Column(String, comment="Raison sociale de la structure")

    # Point de prélèvement d'eau
    # Type de prélèvement :
    type_prelevement = Column(
        Enum(TypePrelevementEnum, name="typeprelevementenum"),
        comment="Type de prélèvement",
    )
    # Numéro de votre arrêté d'AOT :
    numero_arrete_aot = Column(String, comment="Numéro de l’arrêté préfectoral d’AOT")
    # En quelle année les prélèvements que vous allez déclarer ont-ils été réalisés ? :
    annee_prelevement_camion_citerne = Column(
        Integer,
        comment="Pour les camions citernes, année de prélèvement (permet de définir le niveau de précision attendu dans la déclaration)",
    )
    # En quel mois les prélèvements que vous allez déclarer ont-ils été réalisés ? :
    mois_prelevement_camion_citerne = Column(
        String,
        comment="En quel mois les prélèvements que vous allez déclarer ont-ils été réalisés ?",
    )

    # Prélèvement par camion citerne
    # Sur la période concernée par votre déclaration, avez-vous prélevé sur au moins un des points autorisés par votre AOT ? :
    prelevement_sur_periode_camion_citerne = Column(
        Boolean,
        comment="Pour les AOT de camions citernes, indique si des prélèvements ont été réalisés sur la période concernée par la déclaration (mois précédent)",
    )
    #  Votre déclaration concerne-t-elle plusieurs mois (ATTENTION : seules les régularisations peuvent faire l'objet d'une déclaration portant sur plusieurs mois) ? : Modifié le 10/09 08:52
    declaration_plusieurs_mois_camion_citerne = Column(
        Boolean,
        comment="Indique si la déclaration concerne plusieurs mois (seules les régularisations peuvent faire l'objet d'une déclaration portant sur plusieurs mois)",
    )
    # Mois de début de déclaration
    mois_debut_declaration_camion_citerne = Column(
        String,
        comment="Mois de début de déclaration pour les AOT de camions citernes",
    )
    # Mois de fin de déclaration
    mois_fin_declaration_camion_citerne = Column(
        String,
        comment="Mois de fin de déclaration pour les AOT de camions citernes",
    )
    # Mois de déclaration
    mois_declaration_camion_citerne = Column(
        String,
        comment="Mois de déclaration pour les AOT de camions citernes",
    )
    # Dans cette partie, vous allez pouvoir renseigner les volumes pompés en transmettant un tableau de suivi
    volumes_pompes_tableau_suivi_camion_citerne = Column(
        Boolean,
        comment="Indique si les volumes pompés sont renseignés dans un tableau de suivi pour les AOT de camions citernes",
    )
    # Avez-vous prélevé sur au moins un des points autorisés par votre AOT durant l'année 2023 ?
    prelevement_points_autorises_aot_2023 = Column(
        Boolean,
        comment="Avez-vous prélevé sur au moins un des points autorisés par votre AOT durant l'année 2023 ?",
    )
    # Comment souhaitez-vous transmettre vos données ? :
    mode_transmission_donnees_camion_citerne = Column(
        Enum(TypeTransmissionDonneesEnum, name="typetransmissiondonneesenum"),
        comment="Mode de transmission des données pour les AOT camion citerne (une à une, ou au format tableur)",
    )
    # Fichier de tableau de suivi :
    fichier_tableau_suivi_camion_citerne_filename = Column(
        String,
        comment="Nom du fichier de tableau de suivi des prélèvements par camion citerne",
    )
    fichier_tableau_suivi_camion_citerne_url = Column(
        String,
        comment="URL du fichier de tableau de suivi des prélèvements par camion citerne",
    )
    fichier_tableau_suivi_camion_citerne_object_storage = Column(
        String,
        comment="Nom du fichier de tableau de suivi des prélèvements par camion citerne dans l'object storage",
    )
    # Valeur par valeur
    prelevements_citerne_valeur_par_valeur = relationship(
        "PrelevementCiterneValeurParValeur",
        back_populates="dossier",
        cascade="all, delete-orphan",
    )
    # Connaissez-vous précisément les dates et volumes de prélèvement sur chaque point de prélèvement ? :
    details_prelevements_camion_citerne = Column(
        Boolean,
        comment="Indique si le déclarant connait précisément les dates et volumes de prélèvement sur chaque point de prélèvement",
    )

    # Prélèvement AEP ou en ZRE
    donnees_point_de_prelevement_aep_zre = relationship(
        "DonneesPointDePrelevementAPEZRE",
        back_populates="dossier",
        cascade="all, delete-orphan",
    )

    # Autre prélèvement (agricole, domestique...)
    # Nom du point de prélèvement concerné par la déclaration :
    nom_point_prelevement = Column(
        String, comment="Nom du point de prélèvement concerné par la déclaration"
    )
    #  Depuis quand ce point de prélèvement est-il en activité ? :
    date_activation_point_prelevement = Column(
        String, comment="Date d'activation du point de prélèvement"
    )
    # Sur la période concernée par votre déclaration (mois précédent), avez-vous prélevé sur le point de prélèvement autorisé par votre AOT ? :
    prelevement_sur_periode_aot_agricole = Column(
        Boolean,
        comment="Indique si des prélèvements ont été réalisés sur la période concernée par la déclaration (mois précédent)",
    )
    # Relever Index
    releve_index = relationship(
        "ReleverIndex", back_populates="dossier", cascade="all, delete-orphan"
    )

    # Informations sur le compteur
    # Certaines de vos données sont-elles issues d'un compteur volumétrique ? :
    donnees_compteur_volumetrique = Column(
        Boolean,
        comment="Indique sur les données sont issues d’un compteur volumétrique (pour les AOT agricoles)",
    )
    # Souhaitez-vous signaler une panne ou un changement de compteur ? :
    panne_compteur = Column(
        Boolean,
        comment="Indique si une panne ou un changement de compteur est déclarée (pour les AOT agricoles)",
    )
    # Index avant la panne ou le changement :
    index_avant_la_panne_ou_changement_de_compteur = Column(
        Float,
        comment="Index avant la panne ou le changement de compteur (pour les AOT agricoles)",
    )
    # Index après la réparation ou le changement :
    index_apres_la_panne_ou_changement_de_compteur = Column(
        Float,
        comment="Index après la réparation ou le changement de compteur (pour les AOT agricoles)",
    )
    # Numéro de série du compteur :
    numero_serie_compteur = Column(
        String, comment="Numéro de série du compteur (pour les AOT agricoles)"
    )
    # Compteur à lecture directe :
    compteur_lecture_directe = Column(
        Boolean,
        comment="Indique s’il s’agit d’un compteur à lecture directe (pour les AOT agricoles)",
    )
    # Coefficient multiplicateur du compteur :
    coefficient_multiplicateur_compteur = Column(
        String,
        comment="Coefficient multiplicateur du compteur (pour les AOT agricoles)",
    )
    # Pour finir
    # Remarques sur les données transmises
    # Commentaire sur les données transmises :
    commentaire = Column(
        String, comment="Commentaire libre du déclarant sur la déclaration"
    )
    # Retour sur l'utilisation du formulaire
    # Donnez une note sur la facilité de prise en main de l’outil démarches simplifiées :
    note_facilite_utilisation = Column(
        String,
        comment="Donnez une note sur la facilité de prise en main de l’outil démarches simplifiées",
    )
    # Souhaitez-vous apporter une remarque à cette note ? :
    remarque_note = Column(
        String, comment="Souhaitez-vous apporter une remarque à cette note ?"
    )
    # Combien de temps avez-vous passé à remplir ce questionnaire ? :
    temps_remplissage_questionnaire = Column(
        String, comment="Combien de temps avez-vous passé à remplir ce questionnaire ?"
    )
    # Avez-vous une idée ce que qui pourrait être amélioré pour réduire ce temps ? :
    amelioration_temps_remplissage = Column(
        String,
        comment="Avez-vous une idée ce que qui pourrait être amélioré pour réduire ce temps ?",
    )
    #  Combien de temps avez-vous passé au formatage des données (utilisation du modèle de tableur imposé) ?
    temps_formatage_donnees = Column(
        String,
        comment="Combien de temps avez-vous passé au formatage des données (utilisation du modèle de tableur imposé) ?",
    )
    # Qui est la personne qui a fait la déclaration sur Démarches Simplifiées ? :
    declarant_demarche_simplifiee = Column(
        String,
        comment="Qui est la personne qui a fait la déclaration sur Démarches Simplifiées ?",
    )
    #  Qui est la personne qui a téléversé le tableur de données brutes dans l’outil Démarches Simplifiées ?
    televerseur_tableur_brutes = Column(
        String,
        comment="Qui est la personne qui a téléversé le tableur de données brutes dans l’outil Démarches Simplifiées ?",
    )
    # Comment cette personne a-t-elle eu accès au formulaire ?
    acces_formulaire = Column(
        String, comment="Comment cette personne a-t-elle eu accès au formulaire ?"
    )
    # Pour quelles raisons la personne en charge du prélèvement n'a-t-elle pas pu faire la déclaration elle-même ?
    raison_non_declaration_preleveur = Column(
        String,
        comment="Pour quelles raisons la personne en charge du prélèvement n'a-t-elle pas pu faire la déclaration elle-même ?",
    )
    # Souhaiteriez-vous recevoir le 1er de chaque mois un mail vous rappelant l'obligation mensuelle de déclaration ? :
    rappel_obligation_mensuelle_declaration = Column(
        Boolean,
        comment="Souhaiteriez-vous recevoir le 1er de chaque mois un mail vous rappelant l'obligation mensuelle de déclaration ?",
    )
    # Souhaiteriez-vous disposer d’une documentation sur le remplissage de ce formulaire et la façon de remplir le modèle de tableau de données ? :
    demande_documentation = Column(
        String,
        comment="Souhaiteriez-vous disposer d’une documentation sur le remplissage de ce formulaire et la façon de remplir le modèle de tableau de données ?",
    )
    # Sous quelle forme une documentation d’utilisation vous semble la plus utile ? :
    amelioration_documentation = Column(
        String,
        comment="Sous quelle forme une documentation d’utilisation vous semble la plus utile ?",
    )
    # Si vous le souhaitez, vous pouvez nous faire part des informations que vous aimeriez voir figurer dans cet outil de visualisation de données,
    # et qui pourraient vous être utiles pour mieux suivre vos prélèvements au fil du temps. :
    suggestion_informations_visualisation = Column(
        String,
        comment="Si vous le souhaitez, vous pouvez nous faire part des informations que vous aimeriez voir figurer dans cet outil de visualisation de données, "
        + "et qui pourraient vous être utiles pour mieux suivre vos prélèvements au fil du temps.",
    )
    # Accepteriez-vous d’être recontacté.e par la DEAL pour échanger davantage sur le sujet ? :
    acceptation_contact_deal = Column(
        Boolean,
        comment="Accepteriez-vous d’être recontacté.e par la DEAL pour échanger davantage sur le sujet ?",
    )
    # En cochant la présente case, je déclare que les informations que j'ai complété dans le questionnaire sont exactes :
    validation_informations = Column(
        Boolean,
        comment="Déclaration par le préleveur que les informations sont exactes",
    )

    # Champs supprimés conservés pour compatibilité avec les anciennes versions
    date_debut_periode_declaree = Column(
        DateTime, comment="Date du début de la période concernée par la déclaration"
    )
    date_fin_periode_declaree = Column(
        DateTime, comment="Date de fin de la période concernée par la déclaration"
    )

    messages = relationship(
        "Message", back_populates="dossier", cascade="all, delete-orphan"
    )

    avis = relationship("Avis", back_populates="dossier", cascade="all, delete-orphan")

    donnees_prelevement_citerne = relationship(
        "DonneesPrelevementCiterne",
        back_populates="dossier",
        cascade="all, delete-orphan",
    )


class PrelevementCiterneValeurParValeur(Base):
    __tablename__ = "prelevement_citerne_valeur_par_valeur"
    # ID
    id = Column(Integer, primary_key=True, comment="Identifiant unique du prélèvement")
    # Date de prélèvement
    date = Column(DateTime, comment="Date du prélèvement")
    # Date de prélèvement
    annee = Column(Integer, comment="Annee du prélèvement")
    # Volume prélevé
    valeur = Column(Float, comment="Volume prélevé")
    # Point de prélèvement
    nom_point_prelevement = Column(String, comment="Point de prélèvement")

    # Dossier 1-N
    id_dossier = Column(
        Integer,
        ForeignKey("dossier.id", ondelete="CASCADE"),
        comment="Identifiant du dossier",
    )
    dossier = relationship(
        "Dossier", back_populates="prelevements_citerne_valeur_par_valeur"
    )


class DonneesPointDePrelevementAPEZRE(Base):
    __tablename__ = "donnees_point_de_prelevement_aep_zre"
    id = Column(Integer, primary_key=True, comment="Identifiant unique du prélèvement")
    nom_point_prelevement = Column(String, comment="Nom du point de prélèvement")
    prelevement_realise = Column(
        Boolean, comment="Indique si un prélèvement a été réalisé"
    )
    ligne = Column(
        Integer,
        comment="Ordre dans lequel l’index a été déclaré pour une même déclaration",
    )
    fichier_prelevement_filename = Column(
        String, comment="Nom du fichier de prélèvement"
    )
    fichier_prelevement_url = Column(String, comment="URL du fichier de prélèvement")
    fichier_prelevement_object_storage = Column(
        String, comment="Nom du fichier de prélèvement dans l'object storage"
    )
    autre_document_suivi_filename = Column(String, comment="Nom du fichier de suivi")
    autre_document_suivi_url = Column(String, comment="URL du fichier de suivi")
    autre_document_suivi_object_storage = Column(
        String, comment="Nom du fichier de suivi dans l'object storage"
    )

    # Dossier 1-N
    id_dossier = Column(
        Integer,
        ForeignKey("dossier.id", ondelete="CASCADE"),
        comment="Identifiant du dossier",
    )
    dossier = relationship(
        "Dossier", back_populates="donnees_point_de_prelevement_aep_zre"
    )

    donnees_prelevement_aep_zre = relationship(
        "DonneesPrelevementAEPZRE",
        back_populates="donnees_point_de_prelevement_aep_zre",
        cascade="all, delete-orphan",
    )


class ReleverIndex(Base):
    __tablename__ = "relever_index"
    id = Column(
        Integer, primary_key=True, comment="Identifiant unique du relevé d'index"
    )
    date = Column(DateTime, comment="Date du relevé d'index")
    valeur = Column(Float, comment="Index relevé")
    id_dossier = Column(
        Integer,
        ForeignKey("dossier.id", ondelete="CASCADE"),
        comment="Identifiant du dossier",
    )
    dossier = relationship("Dossier", back_populates="releve_index")


class Avis(Base):
    __tablename__ = "avis"
    id = Column(Integer, primary_key=True, comment="Identifiant unique de l'avis")
    question = Column(String, comment="Question de l'avis")
    reponse = Column(String, comment="Réponse à la question de l'avis")
    date_question = Column(DateTime, comment="Date de la question")
    date_reponse = Column(DateTime, comment="Date de la réponse")
    email_claimant = Column(String, comment="Email du demandeur")
    email_expert = Column(String, comment="Email de l'expert")
    pieces_jointes = relationship(
        "AvisPieceJointe", back_populates="avis", cascade="all, delete-orphan"
    )

    id_dossier = Column(
        Integer,
        ForeignKey("dossier.id", ondelete="CASCADE"),
        comment="Identifiant du dossier",
    )
    dossier = relationship("Dossier", back_populates="avis")


class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, comment="Identifiant unique du message")
    date_creation = Column(DateTime, comment="Date du message")
    email = Column(String, comment="Email de l'expéditeur")
    body = Column(String, comment="Contenu du message")

    pieces_jointes = relationship(
        "MessagePieceJointe", back_populates="message", cascade="all, delete-orphan"
    )

    id_dossier = Column(
        Integer,
        ForeignKey("dossier.id", ondelete="CASCADE"),
        comment="Identifiant du dossier",
    )
    dossier = relationship("Dossier", back_populates="messages")


class MessagePieceJointe(Base):
    __tablename__ = "message_piece_jointe"
    id = Column(
        Integer, primary_key=True, comment="Identifiant unique de la pièce jointe"
    )
    filename = Column(String, comment="Nom du fichier")
    url = Column(String, comment="URL du fichier")
    object_storage = Column(String, comment="Nom du fichier dans l'object storage")
    id_message = Column(
        Integer,
        ForeignKey("message.id", ondelete="CASCADE"),
        comment="Identifiant du message",
    )
    message = relationship("Message", back_populates="pieces_jointes")


class AvisPieceJointe(Base):
    __tablename__ = "avis_piece_jointe"
    id = Column(
        Integer, primary_key=True, comment="Identifiant unique de la pièce jointe"
    )
    filename = Column(String, comment="Nom du fichier")
    url = Column(String, comment="URL du fichier")
    object_storage = Column(String, comment="Nom du fichier dans l'object storage")
    id_avis = Column(
        Integer,
        ForeignKey("avis.id", ondelete="CASCADE"),
        comment="Identifiant de l'avis",
    )
    avis = relationship("Avis", back_populates="pieces_jointes")


class DonneesPrelevementCiterne(Base):
    __tablename__ = "donnees_prelevement_citerne"
    id = Column(Integer, primary_key=True, comment="Identifiant unique du prélèvement")
    date_releve = Column(DateTime, comment="Date du relevé")
    volume = Column(Float, comment="Volume prélevé")
    nom_point_prelevement = Column(String, comment="Point de prélèvement")
    id_dossier = Column(
        Integer,
        ForeignKey("dossier.id", ondelete="CASCADE"),
        comment="Identifiant du dossier",
    )

    dossier = relationship("Dossier", back_populates="donnees_prelevement_citerne")


class DonneesPrelevementAEPZRE(Base):
    __tablename__ = "donnees_prelevement_aep_zre"
    date = Column(DateTime, comment="Date et Heure du relevé")
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
    remarque_serie_donnees = Column(String, comment="Remarque sur la série de données")
    nom_point_prelevement = Column(String, comment="Nom du point de prélèvement")
    nom_point_de_prelevement_associe = Column(
        String, comment="Nom du point de prélèvement associé"
    )
    remarque_fonctionnement_point_de_prelevement = Column(
        String, comment="Remarque sur le fonctionnement du point de prélèvement"
    )

    donnees_point_de_prelevement_aep_zre_id = Column(
        Integer,
        ForeignKey("donnees_point_de_prelevement_aep_zre.id", ondelete="CASCADE"),
        comment="Identifiant du point de prélèvement",
    )

    donnees_point_de_prelevement_aep_zre = relationship(
        "DonneesPointDePrelevementAPEZRE", back_populates="donnees_prelevement_aep_zre"
    )
