import enum


class DossierEtatEnum(enum.Enum):
    ACCEPTE = "accepte"
    EN_CONSTRUCTION = "en_construction"
    EN_INSTRUCTION = "en_instruction"
    REFUSE = "refuse"
    SANS_SUITE = "sans_suite"


class DossierSousEtatEnum(enum.Enum):
    EN_ATTENTE_DE_CORRECTION = "en_attente_de_correction"
    CORRIGE = "corrigé"


class CorrectionReasonEnum(str, enum.Enum):
    incorrect = "incorrect"
    incomplete = "incomplete"
    outdated = "outdated"


class ParametreEnum(enum.Enum):
    CHLORURES = "chlorures"
    CONDUCTIVITE = "conductivité"
    DEBIT_PRELEVE = "débit prélevé"
    DEBIT_RESERVE = "débit réservé"
    DEBIT_RESTITUE = "débit restitué"
    NITRATES = "nitrates"
    NIVEAU_EAU = "niveau d’eau"
    PH = "pH"
    RELEVE_INDEX_COMPTEUR = "relevé d’index de compteur"
    SULFATES = "sulfates"
    TEMPERATURE = "température"
    TURBIDITE = "turbidité"
    VOLUME_PRELEVE = "volume prélevé"
    VOLUME_RESTITUE = "volume restitué"
    AUTRE = "autre"


class TypeEnum(enum.Enum):
    VALEUR_BRUTE = "valeur brute"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    MOYENNE = "moyenne"
    MEDIANE = "médiane"
    DIFFERENCE_INDEX = "différence d’index"
    AUTRE = "autre"


class UniteEnum(enum.Enum):
    MICRO_SIEMENS_PAR_CM = "µS/cm"
    DEGRES_CELSIUS = "degrés Celsius"
    LITRE_PAR_SECONDE = "L/s"
    METRE_CUBE_PAR_HEURE = "m³/h"
    METRE_CUBE = "m³"
    METRE_NIVEAU_DE_GRAVITE = "m NGR"
    MILIGRAMME_PAR_LITRE = "mg/L"
    AUTRE = "autre"


class FrequenceEnum(enum.Enum):
    SECONDE = "seconde"
    MINUTE = "minute"
    MINUTES_15 = "15 minutes"
    HEURE = "heure"
    JOUR = "jour"
    MOIS = "mois"
    TRIMESTRE = "trimestre"
    ANNEE = "année"
    AUTRE = "autre"
