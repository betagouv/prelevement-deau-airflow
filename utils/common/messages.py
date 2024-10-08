MESSAGES = {
    "FILE_ERROR": "Une erreur est survenue lors du traitement du fichier.",
    "STANDARD_FILE_FILE_EXTENSION_ERROR": "L'extension du fichier n'est pas valide. Extension attendue: {TABLE_FILES_EXTENSIONS}",
    "FORMAT_FILE_ERROR": "Le format du fichier n'est pas valide.",
    "TABS_ARE_INVALID": "Les onglets du fichier ne sont pas valides. Vérifier que les onglets sont bien nommés. Onglets actuels: {sheets}. Onglets attendus: {expected_sheets}",
    "HEADER_IS_NOT_VALID": "L'en-tête du tableau n'est pas valide. Vérifier que les colonnes sont bien nommées. Colonnes actuelles: {headers}. Colonnes attendues: {expected_headers}",
    "NOM_POINT_DE_PRELEVEMENT_ERROR": "Le nom du point de prélèvement est invalide ou manquant dans l'onglet 'A LIRE'.",
    "ONE_OR_MORE_PARAMETERS_ARE_MISSING": "Un ou plusieurs paramètres sont manquants. les paramètres attendus sont: {parameters}",
    "PARAMETER_VALUE_IS_WRONG": "La parametre {parameter_name} a une valeur incorrecte. La valeur incorrecte est: {incorrect_value}. Les valeurs attendues sont: {expected_values}.",
    "PAPAMETER_IS_MISSING": "La parametre {parameter_name} est manquant. Les valeurs attendues sont: {expected_values}.",
    "DATE_COLUMN_CONTAINS_INVALID_VALUES": "La colonne de date contient des valeurs invalides. Vérifier que la frequence est correcte. Vérifier qu'il n'y a pas de valeurs manquantes.",
    "DATE_COLUMN_IS_NOT_SORTED": "La colonne de date n'est pas triée. Vérifier que les dates des lignes {row1} et {row2} sont triées.",
    "VALUES_ARE_NOT_POSITIVE": "Les valeurs du tableau doivent être positives.",
    "AT_LEAST_ONE_VALUE_SHOULD_BE_PROVIDED_BY_ROW": "Au moins une valeur doit être renseignée. Dans la ligne {row} du tableau.",
    "MISSING_DATE": "La date est manquante dans le tableau. Dans la ligne {row} du tableau.",
    "DATE_FORMAT_ERROR": "La date n'est pas au bon format. Dans la ligne {row} du tableau. La valeur actuelle: '{current_value}'.Vérifier que la date est au format 'DD/MM/YYYY'.",
    "TABLE_IS_EMPTY": "Le tableau est vide. Vérifier que le tableau contient des données.",
    "SEVERAL_FREQUENCY_IN_THE_SAME_SHEET": "Il y a plusieurs fréquences dans le même onglet. Vérifier que la fréquence est unique. les valeurs de fréquence sont: {frequencies}",
    "START_DATE_GREATER_THAN_END_DATE": "La date de début est supérieure à la date de fin. Vérifier que la date de début est inférieure à la date de fin. La date de début est: {start_date}. La date de fin est: {end_date}",
    "DATES_VALUES_ARE_NOT_INCLUDED_IN_DATE_RANGE": "Les dates ne sont pas incluses dans la plage de dates. Vérifier que les dates sont incluses dans la plage de dates. La date de début est: {start_date}. La date de fin est: {end_date}. Les dates non incluses sont: {dates}",
    "PROFONDEUR_NEGATIVE": "La profondeur est négative. Vérifier que la profondeur est positive. La valeur de profondeur incorrecte est: {profondeur}",
    "COLONNE_HEURE_MAL_REMPLIE": "La colonne d'heure est mal remplie. Vérifier que la colonne d'heure est bien remplie. La valeur incorrecte est: {incorrect_value} à la ligne {row}.",
    "PH_VALUE_ERROR": "La valeur du pH est incorrecte. Vérifier que la valeur du pH est correcte et doit être compris entre . La valeur incorrecte est: {incorrect_value} à la ligne {row}.",
    "EMAIL_WRAPPER": """
[Mail de la DEAL] Erreur dans le dossier {dossier_id}

Bonjour,
Vous avez déposé des données de suivi pour un ou des point(s) de prélèvement suivi(s) par la DEAL.
Des tests automatiques sont réalisés sur chaque dossier afin de s'assurer de la conformité et de la cohérence des données. Les erreurs suivantes ont été identifiées sur votre dossier :
{errors}

Nous vous remercions d'apporter les corrections demandées afin de pouvoir valider votre dossier. En cas de difficultés, vous pouvez contacter la DEAL à l'adresse {instructeur_email}, ou en appelant le {instructeur_telephone}.
Bonne journée,
La DEAL""",
}
