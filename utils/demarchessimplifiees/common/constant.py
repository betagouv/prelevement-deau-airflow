from dateutil.relativedelta import relativedelta

from utils.demarchessimplifiees.common.models import FrequenceEnum

champs_text_db_labels = {
    "Champ-3642770": "coordonnees",
    "Champ-3642774": "adresse_email_declarant",
    "Champ-3642775": "numero_telephone_declarant",
    "Champ-3642777": "statut_declarant",
    "Champ-3642778": "raison_sociale_structure",
    "Champ-3888472": "type_prelevement",
    "Champ-3915146": "numero_arrete_aot",
    "Champ-2378771": "nom_point_prelevement",
    "Champ-3888489": "prelevement_citerne",
    "Champ-3988566": "volume_preleve",
    "Champ-3988469": "mode_transmission_donnees_camion_citerne",
    "Champ-3888513": "volumes_pompes_jour",
    "Champ-3988564": "copie_registre_papier",
    "Champ-2379084": "conclusion",
    "Champ-3645094": "commentaire",
    "Champ-3888515": "volumes_annuels_pompes",
    "Champ-3988562": "transmission_extrait_numerique_registre",
    "Champ-3660491": "declaration_point_prelevement",
    "Champ-3642779": "date_activation_point_prelevement",
    "Champ-3888528": "type_autre_prelevement",
    "Champ-3888529": "releve_index_compteur",
    "Champ-3643897": "informations_compteur",
    "Champ-3643910": "numero_serie_compteur",
    "Champ-3914811": "prelevement_icpe",
    "Champ-3642781": "donnees_standardisees",
    "Champ-3888611": "prelevement_aep_zre",
    "Champ-4277890": "mois_prelevement_camion_citerne",
    "Champ-4272683": "note_facilite_utilisation",
    "Champ-4272684": "remarque_note",
    "Champ-4272686": "temps_remplissage_questionnaire",
    "Champ-4272687": "amelioration_temps_remplissage",
    "Champ-4272692": "amelioration_temps_remplissage",
    "Champ-4272689": "temps_formatage_donnees",
    "Champ-4272688": "televersement_tableur_brutes",
    "Champ-4272702": "acces_formulaire",
    "Champ-4272705": "declarant_demarche_simplifiee",
    "Champ-4272709": "raison_non_declaration_preleveur",
    "Champ-4272713": "demande_documentation",
    "Champ-4272714": "amelioration_documentation",
    "Champ-4272723": "suggestion_informations_visualisation",
    # No more used
    # "Champ-4272678": "remarques_donnees_transmises",
    # "Champ-4272680": "retour_utilisation_formulaire",
    # "Champ-4272681": "objectif_collecte_donnees",
    # "Champ-4272720": "developpement_interface_visualisation",
}

champs_checkbox_db_labels = {
    "Champ-2379086": "validation_informations",
    "Champ-3888495": "details_prelevements_camion_citerne",
    "Champ-3660667": "donnees_compteur_volumetrique",
    "Champ-2378798": "compteur_lecture_directe",
    "Champ-2378987": "panne_compteur",
    "Champ-4153004": "prelevement_sur_periode_aot_agricole",
    "Champ-4152855": "prelevement_sur_periode_camion_citerne",
    "Champ-4324950": "prelevement_points_autorises_aot_2023",
    "Champ-4272711": "rappel_obligation_mensuelle_declaration",
    "Champ-4272724": "acceptation_contact_deal",
}

champs_date_db_labels = {
    "Champ-3988441": "date_debut_periode_declaree",
    "Champ-3988442": "date_fin_periode_declaree",
}

champs_integer_number_db_labels = {"Champ-3902209": "annee_prelevement_camion_citerne"}

champs_dropdown_db_labels = {"Champ-4017191": "nom_point_prelevement"}

champs_repetition_db_labels = {
    "Champ-3888490": "volumes_pompes",  # Volumes pompés
    "Champ-3915100": "extrait_registre",  # Extrait de registre
    "Champ-3888549": "releve_index",  # Relevé d'index
    "Champ-3642783": "donnees_point_de_prelevement",  # Données d'un point de prélèvement
}

champs_piece_justificative_db_labels = {
    "Champ-3988475": "fichier_tableau_suivi_camion_citerne"  # Tableau de suivi
}

TABLE_FILES_EXTENSIONS = ["xlsx", "ods"]

extract_file_engine = {
    "xlsx": "openpyxl",
    "ods": "odf",
}

STANDARD_V2_SHEETS = (
    "A_LIRE",
    "NOMENCLATURE",
    "Data_|_T=_15_minutes",
    "Data_|_T=1_jour",
    "Data_|_T=_1_trimestre",
    "Data_|_T=_autre",
)

STANDARD_V2_SHEETS_FREQUENCIES = {
    "Data_|_T=_15_minutes": [FrequenceEnum.MINUTES_15.value],
    "Data_|_T=1_jour": [FrequenceEnum.JOUR.value],
    "Data_|_T=_1_trimestre": [FrequenceEnum.TRIMESTRE.value],
    "Data_|_T=_autre": list(FrequenceEnum._value2member_map_.keys()),
}

PARAMETER_NAME_CHOOSES = {
    "chlorures",
    "conductivité",
    "débit prélevé",
    "débit réservé",
    "débit restitué",
    "nitrates",
    "niveau d’eau",
    "pH",
    "relevé d’index de compteur",
    "sulfates",
    "température",
    "turbidité",
    "volume prélevé",
    "volume restitué",
    "autre",
}

PARAMETER_TYPE_CHOOSES = {
    "valeur brute",
    "minimum",
    "maximum",
    "moyenne",
    "médiane",
    "différence d’index",
    "autre",
}

PARAMETER_UNITE_CHOOSES = {
    "µS/cm",
    "degrés Celsius",
    "L/s",
    "m³/h",
    "m³",
    "m NGR",
    "mg/L",
    "autre",
}

STANDARD_V1_COLUMNS = (
    "Date",
    "412Riv. St Denis La Colline",
    "413Rav. à Jacques (La Montagne)",
    "414Rav. Charpentier",
    "416Ruisseau Emmanuel",
    "417Petite riv St Jean",
    "418Riv. Bras Panon",
    "419Riv. des Galets",
    "420Rav. Bernica",
    "421Bras de la Plaine",
    "422Riv. Des Remparts",
)

FREQUENCIES = {
    "seconde": relativedelta(seconds=1),
    "minute": relativedelta(minutes=1),
    "15 minutes": relativedelta(minutes=15),
    "heure": relativedelta(hours=1),
    "jour": relativedelta(days=1),
    "mois": relativedelta(months=1),
    "trimestre": relativedelta(months=3),
    "année": relativedelta(years=1),
}
