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


class EnrichedFileSerializer(BaseModel):
    id: str
    checksum: str
    type_fichier: str
    nom_fichier: str
    demarches_simplifiees_url: str
    object_storage_key: str


class MessageSerializer(BaseModel):
    id: str
    attachments: List[FileSerializer]
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


# AVIS


class AvisSerializer(BaseModel):
    id: str
    question: str
    reponse: Optional[str] = None
    dateQuestion: datetime.datetime
    dateReponse: Optional[datetime.datetime] = None
    claimant: Profile
    expert: Profile
    attachments: List[EnrichedFileSerializer] = []


class EnrichedAvisSerializer(BaseModel):
    id_avis: str
    id_dossier: int
    question: str
    reponse: Optional[str] = None
    date_question: datetime.datetime
    date_reponse: Optional[datetime.datetime] = None
    claimant_email: str
    expert_email: str
    pieces_jointes: List[EnrichedFileSerializer] = []

    def dict(self, **kwargs):
        return {
            "id_avis": self.id_avis,
            "id_dossier": self.id_dossier,
            "question": self.question,
            "reponse": self.reponse,
            "date_question": self.date_question,
            "date_reponse": self.date_reponse,
            "claimant_email": self.claimant_email,
            "expert_email": self.expert_email,
            "pieces_jointes": "["
            + ",".join([str(f) for f in self.pieces_jointes])
            + "]",
        }


class EnrichedMessageSerializer(BaseModel):
    id_message: str
    id_dossier: int
    email: str
    body: str
    date_creation: datetime.datetime
    pieces_jointes: List[EnrichedFileSerializer] = []

    def dict(self, **kwargs):
        return {
            "id_message": self.id_message,
            "id_dossier": self.id_dossier,
            "email": self.email,
            "body": self.body,
            "date_creation": self.date_creation,
            "pieces_jointes": "["
            + ",".join([str(f) for f in self.pieces_jointes])
            + "]",
        }


class DossierSerializer(BaseModel):
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
    motivation: Optional[str]
    motivationAttachment: Optional[FileSerializer]
    nomMandataire: Optional[str]
    prenomMandataire: Optional[str]
    pdf: Optional[FileSerializer]
    prefilled: bool
    state: DossierState
    traitements: List[Traitement]
    usager: Profile
    champs: List[Champ]
    instructeurs: List[Instructeur]
    groupeInstructeur: GroupeInstructeur
    avis: List[AvisSerializer]
    messages: List[MessageSerializer]


class PageInfo(BaseModel):
    endCursor: Optional[str]
    startCursor: Optional[str]
    hasNextPage: bool
    hasPreviousPage: bool


class DossierConnection(BaseModel):
    pageInfo: PageInfo
    nodes: List[DossierSerializer]


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
    id_dossier: int
    # Email
    adresse_email_connexion: str
    # Civilité
    civilite_declarant: Civilite
    # Nom
    nom_declarant: str
    # Prénom
    prenom_declarant: str
    # Dépôt pour un tiers
    depot_pour_mandataire: bool
    # Nom du mandataire
    nom_mandataire: Optional[str]
    # Prénom du mandataire
    prenom_mandataire: Optional[str]
    # Archivé
    archive: bool
    # État du dossier
    etat_dossier: DossierState
    # Dernière mise à jour le
    derniere_mise_a_jour: datetime.datetime
    # Déposé le
    date_depot: datetime.datetime
    # Passé en instruction le
    date_passage_instruction: datetime.datetime
    # Traité le
    date_traitement: Optional[datetime.datetime] = None
    # Motivation de la décision
    motivation_decision: Optional[str]
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
    adresse_email_declarant: str = ""
    # Champ-3642775
    # Numéro de téléphone
    numero_telephone_declarant: str = ""
    # Champ-3642777
    # Vous formulez cette déclaration en tant que :
    statut_declarant: str = ""
    # Champ-3642778
    # Raison sociale de votre structure
    raison_sociale_structure: str = ""
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
    mode_transmission_donnees_camion_citerne: str = ""
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
    # Champ-4277890
    # En quel mois les prélèvements que vous allez déclarer ont-ils été réalisés ?
    mois_prelevement_camion_citerne: str = ""
    # Champ-4272683
    # Donnez une note sur la facilité de prise en main de l’outil démarches simplifiées
    note_facilite_utilisation: Optional[str] = ""
    # Champ-4272684
    # Souhaitez-vous apporter une remarque à cette note ?
    remarque_note: str = ""
    # Champ-4272686
    # Combien de temps avez-vous passé à remplir ce questionnaire ?
    temps_remplissage_questionnaire: str = ""
    # Champ-4272687,Champ-4272692
    # Avez-vous une idée ce que qui pourrait être amélioré pour réduire ce temps ?
    amelioration_temps_remplissage: str = ""
    # Champ-4272689
    # Combien de temps avez-vous passé au formatage des données (utilisation du modèle de tableur imposé) ?
    temps_formatage_donnees: str = ""
    # Champ-4272688
    # Qui est la personne qui a téléversé le tableur de données brutes dans l’outil Démarches Simplifiées ?
    televersement_tableur_brutes: str = ""
    # Champ-4272702
    # Comment cette personne a-t-elle eu accès au formulaire ?
    acces_formulaire: str = ""
    # Champ-4272705
    # Qui est la personne qui a fait la déclaration sur Démarches Simplifiées ?
    declarant_demarche_simplifiee: str = ""
    # Champ-4272709
    # Pour quelles raisons la personne en charge du prélèvement n'a-t-elle pas pu faire la déclaration elle-même ?
    raison_non_declaration_preleveur: str = ""
    # Champ-4272713
    # Souhaiteriez-vous disposer d’une documentation sur le remplissage de ce formulaire et la façon de remplir le modèle de tableau de données ?
    demande_documentation: str = ""
    # Champ-4272714
    # Sous quelle forme une documentation d’utilisation vous semble la plus utile ?
    amelioration_documentation: str = ""
    # Champ-4272723
    # Si vous le souhaitez, vous pouvez nous faire part des informations que vous aimeriez voir figurer dans cet outil de visualisation de données,
    # et qui pourraient vous être utiles pour mieux suivre vos prélèvements au fil du temps.
    suggestion_informations_visualisation: str = ""

    #################
    # CheckboxChamp #
    #################

    # Champ-2379086
    # En cochant la présente case, je déclare que les informations que j'ai complété dans le questionnaire sont exactes
    validation_informations: Optional[bool] = None
    # Champ-3888495
    # Connaissez-vous précisément les dates et volumes de prélèvement sur chaque point de prélèvement ?
    details_prelevements_camion_citerne: Optional[bool] = None
    # Champ-3660667
    # Certaines de vos données sont-elles issues d'un compteur volumétrique ?
    donnees_compteur_volumetrique: Optional[bool] = None
    # Champ-2378798
    # Compteur à lecture directe
    compteur_lecture_directe: Optional[bool] = None
    # Champ-2378987
    # Souhaitez-vous signaler une panne ou un changement de compteur ?
    panne_compteur: Optional[bool] = None
    # Champ-4153004
    # Sur la période concernée par votre déclaration (mois précédent), avez-vous prélevé sur le point de prélèvement autorisé par votre AOT ?
    prelevement_sur_periode_aot_agricole: Optional[bool] = None
    # Champ-4152855
    # Sur la période concernée par votre déclaration, avez-vous prélevé  sur au moins un des points autorisés par votre AOT ?
    prelevement_sur_periode_camion_citerne: Optional[bool] = None
    # Champ-4324950
    # Avez-vous prélevé sur au moins un des points autorisés par votre AOT durant l'année 2023 ?
    prelevement_points_autorises_aot_2023: Optional[bool] = None
    # Champ-4272711
    # Souhaiteriez-vous recevoir le 1er de chaque mois un mail vous rappelant l'obligation mensuelle de déclaration ?
    rappel_obligation_mensuelle_declaration: Optional[bool] = None
    # Champ-4272724
    # Accepteriez-vous d’être recontacté.e par la DEAL pour échanger davantage sur le sujet ?
    acceptation_contact_deal: Optional[bool] = None

    #############
    # DateChamp #
    #############

    # Champ-3988441
    # Indiquez la date de début de la période concernée par votre déclaration
    date_debut_periode_declaree: Optional[datetime.datetime] = None
    # Champ-3988442
    # Indiquez la date de fin de la période concernée par votre déclaration
    date_fin_periode_declaree: Optional[datetime.datetime] = None

    ######################
    # IntegerNumberChamp #
    ######################

    # Champ-3902209
    # En quelle année les prélèvements que vous allez déclarer ont-ils été réalisés ?
    annee_prelevement_camion_citerne: Optional[int] = None

    #############################
    # MultipleDropDownListChamp #
    #############################

    # Champ-2378771 string
    # Champ-4017191
    # Nom du point de prélèvement concerné par la déclaration
    nom_point_prelevement: Union[str, List[str]] = ""

    # Champ-3988475
    # Tableau de suivi
    fichier_tableau_suivi_camion_citerne: List[EnrichedFileSerializer] = []

    def dict(self):
        return {
            "id_dossier": self.id_dossier,
            "adresse_email_connexion": self.adresse_email_connexion,
            "civilite_declarant": self.civilite_declarant.value,
            "nom_declarant": self.nom_declarant,
            "prenom_declarant": self.prenom_declarant,
            "depot_pour_mandataire": self.depot_pour_mandataire,
            "nom_mandataire": self.nom_mandataire,
            "prenom_mandataire": self.prenom_mandataire,
            "archive": self.archive,
            "etat_dossier": self.etat_dossier.value,
            "derniere_mise_a_jour": self.derniere_mise_a_jour,
            "date_depot": self.date_depot,
            "date_passage_instruction": self.date_passage_instruction,
            "date_traitement": self.date_traitement,
            "motivation_decision": self.motivation_decision,
            "instructeurs": ", ".join([i.email for i in self.instructeurs]),
            "groupe_instructeur": self.groupe_instructeur,
            "coordonnees": self.coordonnees,
            "adresse_email_declarant": self.adresse_email_declarant,
            "numero_telephone_declarant": self.numero_telephone_declarant,
            "statut_declarant": self.statut_declarant,
            "raison_sociale_structure": self.raison_sociale_structure,
            "type_prelevement": self.type_prelevement,
            "numero_arrete_aot": self.numero_arrete_aot,
            "prelevement_citerne": self.prelevement_citerne,
            "volume_preleve": self.volume_preleve,
            "mode_transmission_donnees_camion_citerne": self.mode_transmission_donnees_camion_citerne,
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
            "mois_prelevement_camion_citerne": self.mois_prelevement_camion_citerne,
            "note_facilite_utilisation": self.note_facilite_utilisation,
            "remarque_note": self.remarque_note,
            "temps_remplissage_questionnaire": self.temps_remplissage_questionnaire,
            "amelioration_temps_remplissage": self.amelioration_temps_remplissage,
            "temps_formatage_donnees": self.temps_formatage_donnees,
            "televersement_tableur_brutes": self.televersement_tableur_brutes,
            "acces_formulaire": self.acces_formulaire,
            "declarant_demarche_simplifiee": self.declarant_demarche_simplifiee,
            "raison_non_declaration_preleveur": self.raison_non_declaration_preleveur,
            "demande_documentation": self.demande_documentation,
            "amelioration_documentation": self.amelioration_documentation,
            "suggestion_informations_visualisation": self.suggestion_informations_visualisation,
            "validation_informations": self.validation_informations,
            "details_prelevements_camion_citerne": self.details_prelevements_camion_citerne,
            "donnees_compteur_volumetrique": self.donnees_compteur_volumetrique,
            "compteur_lecture_directe": self.compteur_lecture_directe,
            "panne_compteur": self.panne_compteur,
            "prelevement_sur_periode_aot_agricole": self.prelevement_sur_periode_aot_agricole,
            "prelevement_sur_periode_camion_citerne": self.prelevement_sur_periode_camion_citerne,
            "prelevement_points_autorises_aot_2023": self.prelevement_points_autorises_aot_2023,
            "rappel_obligation_mensuelle_declaration": self.rappel_obligation_mensuelle_declaration,
            "acceptation_contact_deal": self.acceptation_contact_deal,
            "date_debut_periode_declaree": self.date_debut_periode_declaree,
            "date_fin_periode_declaree": self.date_fin_periode_declaree,
            "annee_prelevement_camion_citerne": self.annee_prelevement_camion_citerne,
            "nom_point_prelevement": self.nom_point_prelevement,
            "fichier_tableau_suivi_camion_citerne": str(
                self.fichier_tableau_suivi_camion_citerne
            ),
        }


class ReleveIndexSerializer(BaseModel):
    # Dossier ID
    id_dossier: int
    # Ligne
    ligne: int
    # Champ-3888598
    # Date
    date_releve_index: datetime.datetime
    # Champ-3888599
    # index
    releve_index: float

    def dict(self, **kwargs):
        return {
            "id_dossier": self.id_dossier,
            "ligne": self.ligne,
            "date_releve_index": self.date_releve_index,
            "releve_index": self.releve_index,
        }


class VolumesPompesSerializer(BaseModel):
    # Dossier ID
    id_dossier: int
    # Ligne
    ligne: int
    # Champ-3888497
    # point de prélèvement
    point_prelevement_camion_citerne: Optional[str]
    # Champ-3888496
    # Date
    date_prelevement_camion_citerne: Optional[datetime.date] = None
    # Champ-3888520
    # Annee
    annee_prelevement_camion_citerne_2: Optional[int] = None
    # Champ-3888512
    # Volume pompé (m3)
    volumes_pompes_camions_citernes: Optional[float]

    def dict(self, **kwargs):
        return {
            "id_dossier": self.id_dossier,
            "ligne": self.ligne,
            "point_prelevement_camion_citerne": self.point_prelevement_camion_citerne,
            "date_prelevement_camion_citerne": self.date_prelevement_camion_citerne,
            "annee_prelevement_camion_citerne_2": self.annee_prelevement_camion_citerne_2,
            "volumes_pompes_camions_citernes": self.volumes_pompes_camions_citernes,
        }


class ExtraitDeRegistreSerializer(BaseModel):
    # Dossier ID
    id_dossier: int
    # Ligne
    ligne: int
    # Champ-3915102
    # Extrait de registre
    extraits_registres_papiers: List[EnrichedFileSerializer] = []

    def dict(self, **kwargs):
        return {
            "id_dossier": self.id_dossier,
            "ligne": self.ligne,
            "extraits_registres_papiers": str(self.extraits_registres_papiers),
        }


class DonneesPointDePrelevementSerializer(BaseModel):
    # Dossier ID
    id_dossier: int
    # Ligne
    ligne: int
    # Champ-4017191
    # point de prélèvement
    nom_point_prelevement: List[str] = []
    # Champ-3642817
    # Données standardisées
    fichiers_tableurs: List[EnrichedFileSerializer] = []
    # Champ-4017531
    # Autres documents
    fichiers_autres_documents: List[EnrichedFileSerializer] = []

    def dict(self, **kwargs):
        return {
            "id_dossier": self.id_dossier,
            "ligne": self.ligne,
            "nom_point_prelevement": self.nom_point_prelevement,
            "fichiers_tableurs": str(self.fichiers_tableurs),
            "fichiers_autres_documents": str(self.fichiers_autres_documents),
        }
