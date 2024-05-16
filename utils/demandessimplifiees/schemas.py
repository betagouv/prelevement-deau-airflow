import datetime
import enum
from typing import List, Optional, Union

from pydantic import BaseModel


class DossierState(enum.Enum):
    ACCEPTE = "accepte"
    EN_CONSTRUCTION = "en_construction"
    EN_INSTRUCTION = "en_instruction"
    REFUSE = "refuse"
    SANS_SUITE = "sans_suite"


class Civilite(enum.Enum):
    M = "M"
    Mme = "Mme"


class DemarcheState(enum.Enum):
    BROUILLON = "brouillon"
    CLOSE = "close"
    DEPUBLIEE = "depubliee"
    PUBLIEE = "publiee"


class DossierDeclarativeState(enum.Enum):
    ACCEPTE = "accepte"
    EN_INSTRUCTION = "en_instruction"


class ChampType(enum.Enum):
    CHECKBOX = "CheckboxChamp"
    DATE = "DateChamp"
    INTEGER_NUMBER = "IntegerNumberChamp"
    TEXT = "TextChamp"
    PIECE_JUSTIFICATIVE = "PieceJustificativeChamp"
    REPETITION = "RepetitionChamp"
    DECIMAL_NUMBER = "DecimalNumberChamp"
    MULTIPLE_DROPDOWN_LIST = "MultipleDropDownListChamp"


class Association(BaseModel):
    dateCreation: Optional[datetime.datetime]
    dateDeclaration: Optional[datetime.datetime]
    datePublication: Optional[datetime.datetime]
    objet: Optional[str]
    rna: str
    titre: str


class Effectif(BaseModel):
    nb: float
    periode: str


class Demandeur(BaseModel):
    civilite: Civilite
    nom: Optional[str]
    prenom: Optional[str]
    email: Optional[str]


class Revision(BaseModel):
    id: str


class DemarcheRevision(BaseModel):
    revision: Revision


class File(BaseModel):
    checksum: str
    contentType: str
    createdAt: datetime.datetime
    filename: str
    url: str


class Message(BaseModel):
    id: str
    attachments: List[File]
    body: str
    createdAt: datetime.datetime
    email: str


class Traitement(BaseModel):
    dateTraitement: datetime.datetime
    emailAgentTraitant: Optional[str]
    motivation: Optional[str]
    state: DossierState


class Profile(BaseModel):
    email: str


class BasicChamp(BaseModel):
    id: str
    champDescriptorId: str
    label: str
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
    files: List[File]

    def __str__(self):
        return ";".join([f.url for f in self.files])


class MultipleDropDownListChamp(BasicChamp):
    values: List[str]


Champ = Union[
    TextChamp, CheckboxChamp, DateChamp, IntegerNumberChamp, PieceJustificativeChamp, 'RepetitionChamp', DecimalNumberChamp, MultipleDropDownListChamp]


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


# AVIS

class Avis(BaseModel):
    id: str
    question: str
    reponse: Optional[str] = None
    dateQuestion: datetime.datetime
    dateReponse: Optional[datetime.datetime] = None
    claimant: Profile
    expert: Profile
    attachments: List[File] = []


class EnrichedAvis(Avis):
    dossier_id: int


class Dossier(BaseModel):
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
    dateTraitement: Optional[datetime.datetime]
    demandeur: Optional[Demandeur]
    demarche: DemarcheRevision
    deposeParUnTiers: bool
    messages: List[Message]
    motivation: Optional[str]
    motivationAttachment: Optional[File]
    nomMandataire: Optional[str]
    prenomMandataire: Optional[str]
    pdf: Optional[File]
    prefilled: bool
    state: DossierState
    traitements: List[Traitement]
    usager: Profile
    champs: List[Champ]
    instructeurs: List[Instructeur]
    groupeInstructeur: GroupeInstructeur
    avis: List[Avis]


class PageInfo(BaseModel):
    endCursor: Optional[str]
    startCursor: Optional[str]
    hasNextPage: bool
    hasPreviousPage: bool


class DossierConnection(BaseModel):
    pageInfo: PageInfo
    nodes: List[Dossier]


class ChorusConfiguration(BaseModel):
    centreDeCout: str
    domaineFonctionnel: str
    referentielDeProgrammation: str


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


class PreprocessedDossierSerializer(BaseModel):
    # ID
    number: int
    # Email
    email: str
    # Civilité
    civilite: Civilite
    # Nom
    nom: str
    # Prénom
    prenom: str
    # Dépôt pour un tiers
    deposeParUnTiers: bool
    # Nom du mandataire
    nomMandataire: Optional[str]
    # Prénom du mandataire
    prenomMandataire: Optional[str]
    # Archivé
    archived: bool
    # État du dossier
    state: DossierState
    # Dernière mise à jour le
    dateDerniereModification: datetime.datetime
    # Déposé le
    dateDepot: datetime.datetime
    # Passé en instruction le
    datePassageEnInstruction: datetime.datetime
    # Traité le
    dateTraitement: Optional[datetime.datetime] = None
    # Motivation de la décision
    motivation: Optional[str]
    # Instructeurs
    instructeurs: List[Instructeur]
    # Groupe instructeur
    groupe_instructeur: str

    #############
    # TextChamp #
    #############

    # Champ-3642770
    # Vos coordonnées
    coordonnees: str = ""
    # Champ-3642774
    # Adresse électronique
    adresse_email: str = ""
    # Champ-3642775
    # Numéro de téléphone
    numero_telephone: str = ""
    # Champ-3642777
    # Vous formulez cette déclaration en tant que :
    statut_declarant: str = ""
    # Champ-3642778
    # Raison sociale de votre structure
    raison_sociale_structure: str = ""
    # Champ-2378853
    # Point de prélèvement d'eau
    point_prelevement_eau: str = ""
    # Champ-3888472
    # Type de prélèvement
    type_prelevement: str = ""
    # Champ-3915146
    # Numéro de votre arrêté d'AOT
    numero_arrete_aot: str = ""
    # Champ-3888489
    # Prélèvement par camion citerne
    prelevement_citerne: str = ""
    # Champ-3988566
    # Remontée des volumes prélevés
    volume_preleve: str = ""
    # Champ-3988469
    # Comment souhaitez-vous transmettre vos données ?
    mode_transmission_donnees: str = ""
    # Champ-3888513
    # Dans cette partie, vous allez pouvoir renseigner les volumes pompés par jour sur chaque point de prélèvement
    volumes_pompes_jour: str = ""
    # Champ-3988564
    # Copie du registre papier
    copie_registre_papier: str = ""
    # Champ-2379084
    # Pour finir
    conclusion: str = ""
    # Champ-3645094
    # Commentaire
    commentaire: str = ""
    # Champ-3888515
    # Dans cette partie, vous allez pouvoir renseigner les volumes annuels pompés sur chaque point de prélèvement
    volumes_annuels_pompes: str = ""
    # Champ-3988562
    # Dans cette partie, vous allez pouvoir renseigner les volumes pompés en transmettant un tableau de suivi
    transmission_extrait_numerique_registre: str = ""
    # Champ-3660491
    # Une déclaration doit être faite par point de prélèvement d'eau
    declaration_point_prelevement: str = ""
    # Champ-3642779
    # Depuis quand ce point de prélèvement est-il en activité ?
    date_activation_point_prelevement: str = ""
    # Champ-3888528
    # Autre prélèvement (agricole, domestique...)
    type_autre_prelevement: str = ""
    # Champ-3888529
    # Dans cette partie, vous allez pouvoir renseigner les index lus sur votre compteur à différentes dates
    releve_index_compteur: str = ""
    # Champ-3643897
    # Informations sur le compteur
    informations_compteur: str = ""
    # Champ-3643910
    # Numéro de série du compteur
    numero_serie_compteur: str = ""
    # Champ-3914811
    # Prélèvement ICPE (hors ZRE)
    prelevement_icpe: str = ""
    # Champ-3642781
    # Dans cette partie, vous allez pouvoir transmettre dans un fichier de données standardisé les données relatives aux points de prélèvement concernés par cette déclaration
    donnees_standardisees: str = ""
    # Champ-3888611
    # Prélèvement AEP ou en ZRE
    prelevement_aep_zre: str = ""

    #################
    # CheckboxChamp #
    #################

    # Champ-2379086
    # En cochant la présente case, je déclare que les informations que j'ai complété dans le questionnaire sont exactes
    validation_informations: Optional[bool] = None
    # Champ-3888495
    # Connaissez-vous précisément les dates et volumes de prélèvement sur chaque point de prélèvement ?
    details_prelevements: Optional[bool] = None
    # Champ-3660667
    # Certaines de vos données sont-elles issues d'un compteur volumétrique ?
    donnees_compteur_volumetrique: Optional[bool] = None
    # Champ-2378798
    # Compteur à lecture directe
    compteur_lecture_directe: Optional[bool] = None
    # Champ-2378987
    # Souhaitez-vous signaler une panne ou un changement de compteur ?
    signalement_panne_compteur: Optional[bool] = None
    # Champ-4153004
    # Sur la période concernée par votre déclaration (mois précédent), avez-vous prélevé sur le point de prélèvement autorisé par votre AOT ?
    prelevement_autorise_mois_precedent: Optional[bool] = None
    # Champ-4152855
    # Sur la période concernée par votre déclaration, avez-vous prélevé  sur au moins un des points autorisés par votre AOT ?
    au_moins_un_prelevement: Optional[bool] = None

    #############
    # DateChamp #
    #############

    # Champ-3988441
    # Indiquez la date de début de la période concernée par votre déclaration
    date_debut_declaration: Optional[datetime.datetime] = None
    # Champ-3988442
    # Indiquez la date de fin de la période concernée par votre déclaration
    date_fin_declaration: Optional[datetime.datetime] = None

    ######################
    # IntegerNumberChamp #
    ######################

    # Champ-3902209
    # En quelle année les prélèvements que vous allez déclarer ont-ils été réalisés ?
    annee_prelevement: Optional[int] = None

    #############################
    # MultipleDropDownListChamp #
    #############################

    # Champ-2378771 string
    # Champ-4017191
    # Nom du point de prélèvement concerné par la déclaration
    nom_point_prelevement: Union[str, List[str]] = ""

    def dict(self):
        return {
            "number": self.number,
            "email": self.email,
            "civilite": self.civilite.value,
            "nom": self.nom,
            "prenom": self.prenom,
            "deposeParUnTiers": self.deposeParUnTiers,
            "nomMandataire": self.nomMandataire,
            "prenomMandataire": self.prenomMandataire,
            "archived": self.archived,
            "state": self.state.value,
            "dateDerniereModification": self.dateDerniereModification,
            "dateDepot": self.dateDepot,
            "datePassageEnInstruction": self.datePassageEnInstruction,
            "dateTraitement": self.dateTraitement,
            "motivation": self.motivation,
            "instructeurs": ", ".join([i.email for i in self.instructeurs]),
            "groupe_instructeur": self.groupe_instructeur,
            "coordonnees": self.coordonnees,
            "adresse_email": self.adresse_email,
            "numero_telephone": self.numero_telephone,
            "statut_declarant": self.statut_declarant,
            "raison_sociale_structure": self.raison_sociale_structure,
            "point_prelevement_eau": self.point_prelevement_eau,
            "type_prelevement": self.type_prelevement,
            "numero_arrete_aot": self.numero_arrete_aot,
            "prelevement_citerne": self.prelevement_citerne,
            "volume_preleve": self.volume_preleve,
            "mode_transmission_donnees": self.mode_transmission_donnees,
            "volumes_pompes_jour": self.volumes_pompes_jour,
            "copie_registre_papier": self.copie_registre_papier,
            "conclusion": self.conclusion,
            "commentaire": self.commentaire,
            "volumes_annuels_pompes": self.volumes_annuels_pompes,
            "transmission_extrait_numerique_registre": self.transmission_extrait_numerique_registre,
            "declaration_point_prelevement": self.declaration_point_prelevement,
            "date_activation_point_prelevement": self.date_activation_point_prelevement,
            "type_autre_prelevement": self.type_autre_prelevement,
            "releve_index_compteur": self.releve_index_compteur,
            "informations_compteur": self.informations_compteur,
            "numero_serie_compteur": self.numero_serie_compteur,
            "prelevement_icpe": self.prelevement_icpe,
            "donnees_standardisees": self.donnees_standardisees,
            "prelevement_aep_zre": self.prelevement_aep_zre,
            "validation_informations": self.validation_informations,
            "details_prelevements": self.details_prelevements,
            "donnees_compteur_volumetrique": self.donnees_compteur_volumetrique,
            "compteur_lecture_directe": self.compteur_lecture_directe,
            "signalement_panne_compteur": self.signalement_panne_compteur,
            "prelevement_autorise_mois_precedent": self.prelevement_autorise_mois_precedent,
            "au_moins_un_prelevement": self.au_moins_un_prelevement,
            "date_debut_declaration": self.date_debut_declaration,
            "date_fin_declaration": self.date_fin_declaration,
            "annee_prelevement": self.annee_prelevement,
            "nom_point_prelevement": self.nom_point_prelevement
        }


class ReleveIndexSerializer(BaseModel):
    # Dossier ID
    dossier_id: int
    # Ligne
    ligne: int
    # Champ-3888598
    # Date
    date: datetime.datetime
    # Champ-3888599
    # index
    index: float

    def dict(self, **kwargs):
        return {
            "dossier_id": self.dossier_id,
            "ligne": self.ligne,
            "date": self.date,
            "index": self.index,
        }


class VolumesPompesSerializer(BaseModel):
    # Dossier ID
    dossier_id: int
    # Ligne
    ligne: int
    # Champ-3888497
    # point de prélèvement
    point_prelevement: Optional[str]
    # Champ-3888496
    # Date
    date: Optional[datetime.date] = None
    # Champ-3888520
    # Annee
    annee: Optional[int] = None
    # Champ-3888512
    # Volume pompé (m3)
    volume_pompe: Optional[float]

    def dict(self, **kwargs):
        return {
            "dossier_id": self.dossier_id,
            "ligne": self.ligne,
            "point_prelevement": self.point_prelevement,
            "date": self.date,
            "annee": self.annee,
            "volume_pompe": self.volume_pompe,
        }


class ExtraitDeRegistreSerializer(BaseModel):
    # Dossier ID
    dossier_id: int
    # Ligne
    ligne: int
    # Champ-3915102
    # Extrait de registre
    extrait_registre: PieceJustificativeChamp

    def dict(self, **kwargs):
        return {
            "dossier_id": self.dossier_id,
            "ligne": self.ligne,
            "extrait_registre": str(self.extrait_registre),
        }


class DonneesPointDePrelevementSerializer(BaseModel):
    # Dossier ID
    dossier_id: int
    # Ligne
    ligne: int
    # Champ-4017191
    # point de prélèvement
    point_prelevement: List[str] = []
    # Champ-3642817
    # Données standardisées
    donnees_standardisees: PieceJustificativeChamp
    # Champ-4017531
    # Autres documents
    autres_documents: PieceJustificativeChamp

    def dict(self, **kwargs):
        return {
            "dossier_id": self.dossier_id,
            "ligne": self.ligne,
            "point_prelevement": self.point_prelevement,
            "donnees_standardisees": str(self.donnees_standardisees),
            "autres_documents": str(self.autres_documents),
        }
