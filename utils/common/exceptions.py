from utils.demarchessimplifiees.constant import TABLE_FILES_EXTENSIONS


class FileError(Exception):
    MESSAGE = "Une erreur est survenue lors du traitement du fichier."

    def __init__(self, email, id_dossier, file_name, sheet_name=None):
        super().__init__(email, id_dossier)
        self.file_name = file_name
        self.email = email
        self.id_dossier = id_dossier
        self.sheet_name = sheet_name


class StandardFileFileExtensionError(FileError):
    MESSAGE = f"L'extension du fichier n'est pas valide. Extension attendue: {TABLE_FILES_EXTENSIONS}"


class StandardFileFormatError(FileError):
    MESSAGE = "Le format du fichier n'est pas valide."


class StandardFileProcessingError(FileError):
    MESSAGE = "Une erreur est survenue lors du traitement du fichier."


class StandardFileNomPointDePrelevementError(FileError):
    MESSAGE = "Le nom du point de prélèvement est invalide."


class StandardFileParametersIsMissingError(FileError):
    MESSAGE = "Un ou plusieurs paramètres sont manquants."


class StandardFileParametersBadValueError(FileError):
    MESSAGE = "Un ou plusieurs paramètres ont une valeur incorrecte."

    def __init__(self, email, id_dossier, file_name, sheet_name, parameter_name):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.parameter_name = parameter_name


class StandardFileDateAndHourColumnsBadValueError(FileError):
    MESSAGE = (
        "Les colonnes de date et d'heure ne correspondent pas aux valeurs attendu."
    )


class DateColumnContainsInvalidValuesError(FileError):
    MESSAGE = (
        "La colonne de date contient des valeurs invalides. "
        + "Vérifier que la frequence est correcte."
        + "Vérifier qu'il n'y a pas de valeurs manquantes."
    )


class DateColumnContainsDuplicateValuesError(FileError):
    MESSAGE = "La colonne de date contient des valeurs dupliquées."


class ValuesAreNotPositiveError(FileError):
    MESSAGE = "Les valeurs du tableau doivent être positives."


class AtLeastOneValueShouldBeProvidedByRowError(FileError):
    MESSAGE = "Au moins une valeur doit être renseignée."
