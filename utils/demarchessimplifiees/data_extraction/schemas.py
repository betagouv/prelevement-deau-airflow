import datetime
import enum
from typing import List, Optional, Union

from pydantic import BaseModel


class DossierEtatEnum(enum.Enum):
    ACCEPTE = "accepte"
    EN_CONSTRUCTION = "en_construction"
    EN_INSTRUCTION = "en_instruction"
    REFUSE = "refuse"
    SANS_SUITE = "sans_suite"


class DossierSousEtatEnum(enum.Enum):
    EN_ATTENTE_DE_CORRECTION = "en_attente_de_correction"
    CORRIGE = "corrigé"


class TypePrelevementEnum(enum.Enum):
    PRELEVEMENT_CAMION_CITERNE = "Prélèvement par camion citerne"
    PRELEVEMENT_APE_ZRE = "Prélèvement AEP ou en ZRE"
    PRELEVEMENT_ICPE_HORS_ZRE = "Prélèvement ICPE hors ZRE"
    PRELEVEMENT_AUTRE = "Autre prélèvement (agricole, domestique...)"


class TypeTransmissionDonneesEnum(enum.Enum):
    TABLEAU_SUIVI = "En déposant un tableau de suivi au format tableur (tableau Excel, modèle à télécharger ci-après)"
    VALEUR_PAR_VALEUR = "En renseignant les données une à une"


class Traitement(BaseModel):
    dateTraitement: datetime.datetime
    emailAgentTraitant: Optional[str]
    motivation: Optional[str]
    state: DossierEtatEnum


class DemarcheState(enum.Enum):
    BROUILLON = "brouillon"
    CLOSE = "close"
    DEPUBLIEE = "depubliee"
    PUBLIEE = "publiee"


class ChampType(enum.Enum):
    CHECKBOX = "CheckboxChamp"
    DATE = "DateChamp"
    INTEGER_NUMBER = "IntegerNumberChamp"
    TEXT = "TextChamp"
    PIECE_JUSTIFICATIVE = "PieceJustificativeChamp"
    REPETITION = "RepetitionChamp"
    DECIMAL_NUMBER = "DecimalNumberChamp"
    MULTIPLE_DROPDOWN_LIST = "MultipleDropDownListChamp"


class Profile(BaseModel):
    email: str


class DossierDeclarativeState(enum.Enum):
    ACCEPTE = "accepte"
    EN_INSTRUCTION = "en_instruction"


class Civilite(enum.Enum):
    M = "M"
    Mme = "Mme"


class ChorusConfiguration(BaseModel):
    centreDeCout: str
    domaineFonctionnel: str
    referentielDeProgrammation: str


class PageInfo(BaseModel):
    endCursor: Optional[str]
    startCursor: Optional[str]
    hasNextPage: bool
    hasPreviousPage: bool


class Demandeur(BaseModel):
    civilite: Civilite
    nom: Optional[str]
    prenom: Optional[str]
    email: Optional[str]


class Revision(BaseModel):
    id: str


class DemarcheRevision(BaseModel):
    revision: Revision


class FileSerializer(BaseModel):
    checksum: str
    contentType: str
    createdAt: datetime.datetime
    filename: str
    url: str

    def dict(self, **kwargs):
        return {
            "checksum": self.checksum,
            "contentType": self.contentType,
            "createdAt": self.createdAt,
            "filename": self.filename,
            "url": self.url,
        }

    def __str__(self):
        return str(self.dict())


class BasicChamp(BaseModel):
    id: Optional[str]
    champDescriptorId: Optional[str]
    label: Optional[str]
    stringValue: Optional[str] = None  # Make stringValue optional
    updatedAt: datetime.datetime
    prefilled: bool
    champType: ChampType


class TextChamp(BasicChamp):
    pass


class CheckboxChamp(BasicChamp):
    checked: bool


class DecimalNumberChamp(BasicChamp):
    decimalNumber: float


class DateChamp(BasicChamp):
    date: datetime.date


class IntegerNumberChamp(BasicChamp):
    integerNumber: int


class PieceJustificativeChamp(BasicChamp):
    files: List[FileSerializer]

    def __str__(self):
        return "[" + ";".join([str(f) for f in self.files]) + "]"


class ListFiles(BaseModel):
    files: List[FileSerializer]


class MultipleDropDownListChamp(BasicChamp):
    values: List[str]


Champ = Union[
    TextChamp,
    CheckboxChamp,
    DateChamp,
    IntegerNumberChamp,
    PieceJustificativeChamp,
    "RepetitionChamp",
    DecimalNumberChamp,
    MultipleDropDownListChamp,
]


class Row(BaseModel):
    champs: List[Champ]


class RepetitionChamp(BasicChamp):
    rows: List[Row]


# INSTRUCTEUR
class Instructeur(BaseModel):
    id: str
    email: str

    def __str__(self):
        return f"({self.id} {self.email})"


class GroupeInstructeur(BaseModel):
    id: str
    number: int
    label: str
    instructeurs: List[Instructeur]


class InputMessageSerializer(BaseModel):
    id: str
    attachments: List[FileSerializer]
    body: str
    createdAt: datetime.datetime
    email: str


# AVIS


class InputAvisSerializer(BaseModel):
    id: str
    question: str
    reponse: Optional[str] = None
    dateQuestion: datetime.datetime
    dateReponse: Optional[datetime.datetime] = None
    claimant: Profile
    expert: Profile
    attachments: List[FileSerializer] = []


class InputDossierSerializer(BaseModel):
    id: str
    number: int
    archived: bool
    attestation: Optional[str]
    dateDepot: datetime.datetime
    dateDerniereModification: datetime.datetime
    dateExpiration: Optional[datetime.datetime]
    datePassageEnConstruction: Optional[datetime.datetime]
    datePassageEnInstruction: Optional[datetime.datetime]
    dateSuppressionParUsager: Optional[datetime.datetime]
    dateDerniereCorrectionEnAttente: Optional[datetime.datetime]
    dateTraitement: Optional[datetime.datetime]
    demandeur: Optional[Demandeur]
    demarche: DemarcheRevision
    deposeParUnTiers: bool
    motivation: Optional[str]
    motivationAttachment: Optional[FileSerializer]
    nomMandataire: Optional[str]
    prenomMandataire: Optional[str]
    pdf: Optional[FileSerializer]
    prefilled: bool
    state: DossierEtatEnum
    traitements: List[Traitement]
    usager: Profile
    champs: List[Champ]
    annotations: List[Champ]
    instructeurs: List[Instructeur]
    groupeInstructeur: GroupeInstructeur
    avis: List[InputAvisSerializer]
    messages: List[InputMessageSerializer]


class DossierConnection(BaseModel):
    pageInfo: PageInfo
    nodes: List[InputDossierSerializer]


class Demarche(BaseModel):
    id: str
    number: int
    title: str
    state: DemarcheState
    declarative: DossierDeclarativeState
    dateCreation: datetime.datetime
    dateFermeture: Optional[datetime.datetime]
    chorusConfiguration: ChorusConfiguration
    dossiers: DossierConnection


class PrelevementCiterneValeurParValeurSerializer(BaseModel):
    nom_point_prelevement: str
    date: Optional[datetime.date] = None
    annee: Optional[int] = None
    valeur: float


class PrelevementAPEZRESerializer(BaseModel):
    ligne: int
    nom_point_prelevement: str
    fichier_prelevement_filename: str
    fichier_prelevement_url: str
    fichier_prelevement_object_storage: str
    autre_document_suivi_filename: Optional[str] = None
    autre_document_suivi_url: Optional[str] = None
    autre_document_suivi_object_storage: Optional[str] = None


class AutrePrelevementSerializer(BaseModel):
    date: datetime.date
    valeur: float


class ReleverIndexSerializer(BaseModel):
    date: datetime.date
    valeur: float


class PieceJointeSerializer(BaseModel):
    filename: str
    url: str
    object_storage: str


class MessageSerializer(BaseModel):
    id: int
    pieces_jointes: List[PieceJointeSerializer]
    body: str
    date_creation: datetime.datetime
    email: str


class AvisSerializer(BaseModel):
    id: int
    question: str
    reponse: Optional[str]
    date_question: datetime.datetime
    date_reponse: Optional[datetime.datetime]
    email_claimant: str
    email_expert: str
    pieces_jointes: List[PieceJointeSerializer]


class DossierSerializer(BaseModel):
    # ID
    id: int
    # Archivé
    archive: bool
    # État du dossier
    etat_dossier: DossierEtatEnum
    # Sous-état du dossier
    sous_etat_dossier: Optional[DossierSousEtatEnum]
    # Dernière mise à jour le
    derniere_mise_a_jour: datetime.datetime
    # Déposé le
    date_depot: datetime.datetime
    # Passé en instruction le
    date_passage_instruction: Optional[datetime.datetime]
    # Date de la dernière correction en attente
    date_derniere_correction_en_attente: Optional[datetime.datetime]
    # Traité le
    date_traitement: Optional[datetime.datetime]
    # Motivation de la décision
    motivation_decision: Optional[str]
    # Instructeurs
    instructeurs: Optional[str]
    # Groupe instructeur
    groupe_instructeur: str

    # Identité du demandeur
    # Email
    adresse_email_connexion: str
    # Civilité
    civilite_declarant: Civilite
    # Nom
    nom_declarant: str
    # Prénom
    prenom_declarant: str
    # Nom du mandataire
    nom_mandataire: Optional[str]
    # Prénom du mandataire
    prenom_mandataire: Optional[str]
    # Dépôt pour un tiers
    depot_pour_mandataire: bool

    # Vos coordonnées
    # Adresse électronique :
    adresse_email_declarant: str
    # Numéro de téléphone :
    numero_telephone_declarant: str
    # Vous formulez cette déclaration en tant que :
    statut_declarant: str
    # Raison sociale de votre structure :
    raison_sociale_structure: Optional[str]

    # Point de prélèvement d'eau
    # Type de prélèvement :
    type_prelevement: TypePrelevementEnum
    # Numéro de votre arrêté d'AOT :
    numero_arrete_aot: Optional[str] = None
    # En quelle année les prélèvements que vous allez déclarer ont-ils été réalisés ? :
    annee_prelevement_camion_citerne: Optional[int] = None
    # En quel mois les prélèvements que vous allez déclarer ont-ils été réalisés ? :
    mois_prelevement_camion_citerne: Optional[str] = None

    # Prélèvement par camion citerne
    # Sur la période concernée par votre déclaration, avez-vous prélevé sur au moins un des points autorisés par votre AOT ? :
    prelevement_sur_periode_camion_citerne: Optional[bool] = None
    # Avez-vous prélevé sur au moins un des points autorisés par votre AOT durant l'année 2023 ?
    prelevement_points_autorises_aot_2023: Optional[bool] = None
    # Comment souhaitez-vous transmettre vos données ? :
    mode_transmission_donnees_camion_citerne: Optional[TypeTransmissionDonneesEnum] = (
        None
    )
    # Fichier de tableau de suivi :
    fichier_tableau_suivi_camion_citerne_filename: Optional[str] = None
    fichier_tableau_suivi_camion_citerne_url: Optional[str] = None
    fichier_tableau_suivi_camion_citerne_object_storage: Optional[str] = None
    # Valeur par valeur
    prelevement_citerne_valeur_par_valeur: List[
        PrelevementCiterneValeurParValeurSerializer
    ] = []
    # Connaissez-vous précisément les dates et volumes de prélèvement sur chaque point de prélèvement ? :
    details_prelevements_camion_citerne: Optional[bool] = None

    # Prélèvement AEP ou en ZRE
    donnees_point_de_prelevement_aep_zre: List[PrelevementAPEZRESerializer] = []

    # Autre prélèvement (agricole, domestique...)
    # Nom du point de prélèvement concerné par la déclaration :
    nom_point_prelevement: Optional[str] = None
    #  Depuis quand ce point de prélèvement est-il en activité ? :
    date_activation_point_prelevement: Optional[str] = None
    # Sur la période concernée par votre déclaration (mois précédent), avez-vous prélevé sur le point de prélèvement autorisé par votre AOT ? :
    prelevement_sur_periode_aot_agricole: Optional[bool] = None
    # Relever Index
    releve_index: List[ReleverIndexSerializer] = []

    # Informations sur le compteur
    # Certaines de vos données sont-elles issues d'un compteur volumétrique ? :
    donnees_compteur_volumetrique: Optional[bool] = None
    # Souhaitez-vous signaler une panne ou un changement de compteur ? :
    panne_compteur: Optional[bool] = None
    # Index avant la panne ou le changement :
    index_avant_la_panne_ou_changement_de_compteur: Optional[float] = None
    # Index après la réparation ou le changement :
    index_apres_la_panne_ou_changement_de_compteur: Optional[float] = None
    # Numéro de série du compteur :
    numero_serie_compteur: Optional[str] = None
    # Compteur à lecture directe :
    compteur_lecture_directe: Optional[bool] = None
    # Coefficient multiplicateur du compteur :
    coefficient_multiplicateur_compteur: Optional[str] = None

    # Pour finir
    # Remarques sur les données transmises
    # Commentaire sur les données transmises :
    commentaire: Optional[str] = None
    # Retour sur l'utilisation du formulaire
    # Donnez une note sur la facilité de prise en main de l’outil démarches simplifiées :
    note_facilite_utilisation: Optional[int] = None
    # Souhaitez-vous apporter une remarque à cette note ? :
    remarque_note: Optional[str] = None
    # Combien de temps avez-vous passé à remplir ce questionnaire ? :
    temps_remplissage_questionnaire: Optional[str] = None
    # Avez-vous une idée ce que qui pourrait être amélioré pour réduire ce temps ? :
    amelioration_temps_remplissage: Optional[str] = None
    #  Combien de temps avez-vous passé au formatage des données (utilisation du modèle de tableur imposé) ?
    temps_formatage_donnees: Optional[str] = None
    # Qui est la personne qui a fait la déclaration sur Démarches Simplifiées ? :
    declarant_demarche_simplifiee: Optional[str] = None
    #  Qui est la personne qui a téléversé le tableur de données brutes dans l’outil Démarches Simplifiées ? :
    televerseur_tableur_brutes: Optional[str] = None
    # Pour quelles raisons la personne en charge du prélèvement n'a-t-elle pas pu faire la déclaration elle-même ?
    raison_non_declaration_preleveur: Optional[str] = None
    # Souhaiteriez-vous recevoir le 1er de chaque mois un mail vous rappelant l'obligation mensuelle de déclaration ? :
    rappel_obligation_mensuelle_declaration: Optional[bool] = None
    # Souhaiteriez-vous disposer d’une documentation sur le remplissage de ce formulaire et la façon de remplir le modèle de tableau de données ? :
    demande_documentation: Optional[str] = None
    # Sous quelle forme une documentation d’utilisation vous semble la plus utile ? :
    amelioration_documentation: Optional[str] = None
    # Si vous le souhaitez, vous pouvez nous faire part des informations que vous aimeriez voir figurer dans cet outil de visualisation de données,
    # et qui pourraient vous être utiles pour mieux suivre vos prélèvements au fil du temps. :
    developpement_interface_visualisation: Optional[str] = None
    # Accepteriez-vous d’être recontacté.e par la DEAL pour échanger davantage sur le sujet ? :
    acceptation_contact_deal: Optional[bool] = None
    # En cochant la présente case, je déclare que les informations que j'ai complété dans le questionnaire sont exactes :
    validation_informations: Optional[bool] = None

    # Champs supprimés conservés pour compatibilité avec les anciennes versions
    date_debut_periode_declaree: Optional[datetime.datetime] = None
    date_fin_periode_declaree: Optional[datetime.datetime] = None
    acces_formulaire: Optional[str] = None
    suggestion_informations_visualisation: Optional[str] = None

    # Messages
    messages: List[MessageSerializer] = []

    # Avis
    avis: List[AvisSerializer] = []
