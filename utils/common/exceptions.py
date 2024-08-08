from utils.common.messages import MESSAGES
from utils.demarchessimplifiees.common.constant import TABLE_FILES_EXTENSIONS


class FileError(Exception):
    MESSAGE = MESSAGES["FILE_ERROR"]

    def __init__(self, email, id_dossier, file_name, sheet_name=None):
        super().__init__(email, id_dossier)
        self.file_name = file_name
        self.email = email
        self.id_dossier = id_dossier
        self.sheet_name = sheet_name

    def get_error_message(self):
        return self.MESSAGE

    def get_message_to_send(self):
        message = f"[{self.id_dossier}]"
        if self.sheet_name:
            message += f" problème sur l'onglet {self.sheet_name} du fichier '{self.file_name}'\n"
        else:
            message += f" problème sur le fichier '{self.file_name}'.\n"
        message += self.get_error_message()
        return message


class StandardFileFileExtensionError(FileError):
    MESSAGE = MESSAGES["STANDARD_FILE_FILE_EXTENSION_ERROR"].format(
        TABLE_FILES_EXTENSIONS=TABLE_FILES_EXTENSIONS
    )


class StandardFileFormatError(FileError):
    MESSAGE = MESSAGES["FORMAT_FILE_ERROR"]


class TableHeadersError(FileError):
    MESSAGE = MESSAGES["HEADER_IS_NOT_VALID"]

    def __init__(
        self, email, id_dossier, file_name, sheet_name, headers, expected_headers
    ):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.headers = headers
        self.expected_headers = expected_headers

    def get_error_message(self):
        return self.MESSAGE.format(
            headers=self.headers, expected_headers=self.expected_headers
        )


class StandardFileNomPointDePrelevementError(FileError):
    MESSAGE = MESSAGES["NOM_POINT_DE_PRELEVEMENT_ERROR"]


class StandardFileParametersIsMissingError(FileError):
    MESSAGE = MESSAGES["ONE_OR_MORE_PARAMETERS_ARE_MISSING"]

    def __init__(self, email, id_dossier, file_name, sheet_name, parameters):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.parameters = parameters

    def get_error_message(self):
        return self.MESSAGE.format(parameters=self.parameters)


class StandardFileParametersBadValueError(FileError):
    MESSAGE = MESSAGES["ONE_OR_MORE_PARAMETERS_HAVE_BAD_VALUE"]

    def __init__(self, email, id_dossier, file_name, sheet_name, parameter_name):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.parameter_name = parameter_name

    def get_error_message(self):
        return self.MESSAGE.format(parameters=self.parameter_name)


class StandardFileDateAndHourColumnsBadValueError(FileError):
    MESSAGE = MESSAGES["DATE_AND_HOUR_COLUMNS_BAD_VALUE"]

    def __init__(self, email, id_dossier, file_name, sheet_name, rows):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.rows = rows

    def get_error_message(self):
        return self.MESSAGE.format(rows=self.rows)


class DateFrequencyMismatchException(FileError):
    MESSAGE = MESSAGES["DATE_FREQUENCY_MISMATCH"]


class DateColumnContainsInvalidValuesError(FileError):
    MESSAGE = MESSAGES["DATE_COLUMN_CONTAINS_INVALID_VALUES"]


class DateColumnContainsDuplicateValuesError(FileError):
    MESSAGE = MESSAGES["DATE_COLUMN_CONTAINS_DUPLICATE_VALUES"]

    def __init__(self, email, id_dossier, file_name, sheet_name, rows):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.rows = rows

    def get_error_message(self):
        return self.MESSAGE.format(rows=self.rows)


class ValuesAreNotPositiveError(FileError):
    MESSAGE = MESSAGES["VALUES_ARE_NOT_POSITIVE"]


class AtLeastOneValueShouldBeProvidedByRowError(FileError):
    MESSAGE = MESSAGES["AT_LEAST_ONE_VALUE_SHOULD_BE_PROVIDED_BY_ROW"]

    def __init__(self, email, id_dossier, file_name, row, sheet_name=None):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.row = row

    def get_error_message(self):
        return self.MESSAGE.format(row=self.row)


class MissingDateError(FileError):
    MESSAGE = MESSAGES["MISSING_DATE"]

    def __init__(self, email, id_dossier, file_name, row, sheet_name=None):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.row = row

    def get_error_message(self):
        return self.MESSAGE.format(row=self.row)


class DateFormatError(FileError):
    MESSAGE = MESSAGES["DATE_FORMAT_ERROR"]

    def __init__(
        self, email, id_dossier, file_name, row, current_value, sheet_name=None
    ):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.row = row
        self.current_value = current_value

    def get_error_message(self):
        return self.MESSAGE.format(row=self.row, current_value=self.current_value)


class TableIsEmptyError(FileError):
    MESSAGE = MESSAGES["TABLE_IS_EMPTY"]

    def __init__(self, email, id_dossier, file_name):
        super().__init__(email, id_dossier, file_name)
