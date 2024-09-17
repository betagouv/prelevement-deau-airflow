from dateutil.relativedelta import relativedelta

from utils.demarchessimplifiees.common.schemas import FrequenceEnum

champs_to_labels = {
    # Vos coordonnées
    # Adresse électronique :
    "Champ-3642774": "adresse_email_declarant",
    # Numéro de téléphone :
    "Champ-3642775": "numero_telephone_declarant",
    # Vous formulez cette déclaration en tant que :
    "Champ-3642777": "statut_declarant",
    # Raison sociale de votre structure :
    "Champ-3642778": "raison_sociale_structure",
    # Point de prélèvement d'eau
    # Type de prélèvement :
    "Champ-3888472": "type_prelevement",
    # Numéro de votre arrêté d'AOT :
    "Champ-3915146": "numero_arrete_aot",
    "Champ-4458483": "numero_arrete_aot",
    # En quelle année les prélèvements que vous allez déclarer ont-ils été réalisés ? :
    "Champ-3902209": "annee_prelevement_camion_citerne",
    # En quel mois les prélèvements que vous allez déclarer ont-ils été réalisés ? :
    "Champ-4277890": "mois_prelevement_camion_citerne",
    # Prélèvement par camion citerne
    # Sur la période concernée par votre déclaration, avez-vous prélevé sur au moins un des points autorisés par votre AOT ? :
    "Champ-4152855": "prelevement_sur_periode_camion_citerne",
    #  Votre déclaration concerne-t-elle plusieurs mois (ATTENTION : seules les régularisations peuvent faire l'objet d'une déclaration portant sur plusieurs mois) ? : Modifié le 10/09 08:52
    "Champ-4460662": "declaration_plusieurs_mois_camion_citerne",  # checked
    "Champ-4489395": "declaration_plusieurs_mois_camion_citerne",  # checked
    # Mois de début de déclaration
    "Champ-4460669": "mois_debut_declaration_camion_citerne",  # string
    "Champ-4489398": "mois_debut_declaration_camion_citerne",  # string
    # Mois de fin de déclaration
    "Champ-4460678": "mois_fin_declaration_camion_citerne",  # string
    "Champ-4489397": "mois_fin_declaration_camion_citerne",  # string
    # Mois de déclaration
    "Champ-4460664": "mois_declaration_camion_citerne",  # string
    # Dans cette partie, vous allez pouvoir renseigner les volumes pompés en transmettant un tableau de suivi
    "Champ-4467020": "volumes_pompes_tableau_suivi_camion_citerne",  # string
    "Champ-4489519": "volumes_pompes_tableau_suivi_camion_citerne",  # string
    # Avez-vous prélevé sur au moins un des points autorisés par votre AOT durant l'année 2023 ?
    "Champ-4324950": "prelevement_points_autorises_aot_2023",
    # Comment souhaitez-vous transmettre vos données ? :
    "Champ-3988469": "mode_transmission_donnees_camion_citerne",
    # Fichier de tableau de suivi :
    "Champ-3988475": "fichier_tableau_suivi_camion_citerne",
    "Champ-4458484": "fichier_tableau_suivi_camion_citerne",
    "Champ-4467021": "fichier_tableau_suivi_camion_citerne",
    # Valeur par valeur & Volumes pompés
    "Champ-3888490": "prelevement_citerne_valeur_par_valeur_tmp",
    "Champ-3888513": "prelevement_citerne_valeur_par_valeur_tmp",
    # Connaissez-vous précisément les dates et volumes de prélèvement sur chaque point de prélèvement ? :
    "Champ-3888495": "details_prelevements_camion_citerne",
    # Prélèvement AEP ou en ZRE
    "Champ-3642783": "donnees_point_de_prelevement_aep_zre_tmp",
    # Autre prélèvement (agricole, domestique...)
    # Nom du point de prélèvement concerné par la déclaration :
    "Champ-2378771": "nom_point_prelevement",
    "Champ-4017191": "nom_point_prelevement",
    "Champ-2378853": "nom_point_prelevement",
    #  Depuis quand ce point de prélèvement est-il en activité ? :
    "Champ-3642779": "date_activation_point_prelevement",
    # Sur la période concernée par votre déclaration (mois précédent), avez-vous prélevé sur le point de prélèvement autorisé par votre AOT ? :
    "Champ-4153004": "prelevement_sur_periode_aot_agricole",
    # Relever Index
    "Champ-3888549": "releve_index_tmp",
    # Informations sur le compteur
    "Champ-3643897": "informations_compteur",
    # Certaines de vos données sont-elles issues d'un compteur volumétrique ? :
    "Champ-3660667": "donnees_compteur_volumetrique",
    # Souhaitez-vous signaler une panne ou un changement de compteur ? :
    "Champ-2378987": "panne_compteur",
    # Index avant la panne ou le changement :
    "Champ-2379029": "index_avant_la_panne_ou_changement_de_compteur",
    # Index après la réparation ou le changement :
    "Champ-2379030": "index_apres_la_panne_ou_changement_de_compteur",
    # Numéro de série du compteur :
    "Champ-3643910": "numero_serie_compteur",
    # Compteur à lecture directe :
    "Champ-2378798": "compteur_lecture_directe",
    # Coefficient multiplicateur du compteur :
    "Champ-2378833": "coefficient_multiplicateur_compteur",
    # Pour finir
    # Remarques sur les données transmises
    # Commentaire sur les données transmises :
    "Champ-3645094": "commentaire",
    # Retour sur l'utilisation du formulaire
    # Donnez une note sur la facilité de prise en main de l’outil démarches simplifiées :
    "Champ-4272683": "note_facilite_utilisation",
    # Souhaitez-vous apporter une remarque à cette note ? :
    "Champ-4272684": "remarque_note",
    # Combien de temps avez-vous passé à remplir ce questionnaire ? :
    "Champ-4272686": "temps_remplissage_questionnaire",
    # Avez-vous une idée ce que qui pourrait être amélioré pour réduire ce temps ? :
    "Champ-4272687": "amelioration_temps_remplissage",
    "Champ-4272692": "amelioration_temps_remplissage",
    #  Combien de temps avez-vous passé au formatage des données (utilisation du modèle de tableur imposé) ?
    "Champ-4272689": "temps_formatage_donnees",
    # Qui est la personne qui a fait la déclaration sur Démarches Simplifiées ? :
    "Champ-4272705": "declarant_demarche_simplifiee",
    #  Qui est la personne qui a téléversé le tableur de données brutes dans l’outil Démarches Simplifiées ? :
    "Champ-4272688": "televerseur_tableur_brutes",
    # Comment cette personne a-t-elle eu accès au formulaire ?
    "Champ-4272702": "acces_formulaire",
    # Pour quelles raisons la personne en charge du prélèvement n'a-t-elle pas pu faire la déclaration elle-même ?
    "Champ-4272709": "raison_non_declaration_preleveur",
    # Souhaiteriez-vous recevoir le 1er de chaque mois un mail vous rappelant l'obligation mensuelle de déclaration ? :
    "Champ-4272711": "rappel_obligation_mensuelle_declaration",
    # Souhaiteriez-vous disposer d’une documentation sur le remplissage de ce formulaire et la façon de remplir le modèle de tableau de données ? :
    "Champ-4272713": "demande_documentation",
    # Sous quelle forme une documentation d’utilisation vous semble la plus utile ? :
    "Champ-4272714": "amelioration_documentation",
    # Si vous le souhaitez, vous pouvez nous faire part des informations que vous aimeriez voir figurer dans cet outil de visualisation de données,
    # et qui pourraient vous être utiles pour mieux suivre vos prélèvements au fil du temps. :
    "Champ-4272720": "suggestion_informations_visualisation",
    "Champ-4272723": "suggestion_informations_visualisation",
    # Accepteriez-vous d’être recontacté.e par la DEAL pour échanger davantage sur le sujet ? :
    "Champ-4272724": "acceptation_contact_deal",
    # En cochant la présente case, je déclare que les informations que j'ai complété dans le questionnaire sont exactes :
    "Champ-2379086": "validation_informations",
    # Champs supprimés mais conservés
    # Date du début de la période concernée par la déclaration
    "Champ-3988441": "date_debut_periode_declaree",
    # Date de fin de la période concernée par la déclaration
    "Champ-3988442": "date_fin_periode_declaree",
    # Champs supprimés
    # Vos coordonnées
    "Champ-3642770": "coordonnees",
    # Remontée des volumes prélevés
    "Champ-3988566": "volume_preleve",
    # "Champ-3888513": "volumes_pompes_jour", => renommé en "prelevement_citerne_valeur_par_valeur_tmp"
    # Copie du registre papier
    "Champ-3988564": "copie_registre_papier",
    # Extrait de registre
    "Champ-3915100": "extrait_registre",
    # Prélèvement par camion citerne
    "Champ-3888489": "prelevement_citerne",
    # Pour finir
    "Champ-2379084": "conclusion",
    # Dans cette partie, vous allez pouvoir renseigner les volumes annuels pompés sur chaque point de prélèvement
    "Champ-3888515": "volumes_annuels_pompes",
    # Dans cette partie, vous allez pouvoir renseigner les volumes pompés en transmettant un extrait numérique de votre registre
    "Champ-3988562": "transmission_extrait_numerique_registre",
    # Une déclaration doit être faite par point de prélèvement d'eau
    "Champ-3660491": "declaration_point_prelevement",
    # Autre prélèvement (agricole, domestique...)
    "Champ-3888528": "type_autre_prelevement",
    # Dans cette partie, vous allez pouvoir renseigner les index lus sur votre compteur à différentes dates
    "Champ-3888529": "releve_index_compteur",
    # Prélèvement ICPE (hors ZRE)
    "Champ-3914811": "prelevement_icpe",
    "Champ-3642781": "donnees_standardisees",
    # Prélèvement AEP ou en ZRE
    "Champ-3888611": "prelevement_aep_zre",
    # Remarques sur les données transmises
    "Champ-4272678": "remarques_donnees_transmises",
    # Retour sur l'utilisation du formulaire
    "Champ-4272680": "retour_utilisation_formulaire",
    # Ce formulaire  permet à l’administration de collecter les données de suivi des prélèvements d'eau
    "Champ-4272681": "objectif_collecte_donnees",
    # Avez-vous déjà renseigné les éléments relatifs à votre compteur lors d'une précédente déclaration (numéro de série et type de compteur) ?
    "Champ-4317248": "compteur_renseigne_precedente_declaration",
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
