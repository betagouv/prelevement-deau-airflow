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


class TabsAreInvalidError(FileError):
    MESSAGE = MESSAGES["TABS_ARE_INVALID"]

    def __init__(self, email, id_dossier, file_name, sheets, expected_sheets):
        super().__init__(email, id_dossier, file_name)
        self.sheets = sheets
        self.expected_sheets = expected_sheets

    def get_error_message(self):
        return self.MESSAGE.format(
            sheets=self.sheets, expected_sheets=self.expected_sheets
        )


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
    MESSAGE = MESSAGES["PARAMETER_VALUE_IS_WRONG"]

    def __init__(
        self,
        email,
        id_dossier,
        file_name,
        sheet_name,
        parameter_name,
        incorrect_value,
        expected_values,
    ):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.parameter_name = parameter_name
        self.expected_values = expected_values
        self.incorrect_value = incorrect_value

    def get_error_message(self):
        return self.MESSAGE.format(
            parameter_name=self.parameter_name,
            incorrect_value=self.incorrect_value,
            expected_values=self.expected_values,
        )


class ParameterIsMissingError(FileError):
    MESSAGE = MESSAGES["PAPAMETER_IS_MISSING"]

    def __init__(
        self, email, id_dossier, file_name, sheet_name, parameter_name, expected_values
    ):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.parameter_name = parameter_name
        self.expected_values = expected_values

    def get_error_message(self):
        return self.MESSAGE.format(
            parameter_name=self.parameter_name, expected_values=self.expected_values
        )


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

    def __init__(self, email, id_dossier, file_name, sheet_name, duplicated_dates):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.duplicated_dates = [
            duplicate_date.strftime("%d/%m/%Y") for duplicate_date in duplicated_dates
        ]

    def get_error_message(self):
        return self.MESSAGE.format(duplicated_dates=self.duplicated_dates)


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


class SeveralFrequencyInTheSameSheetError(FileError):
    MESSAGE = MESSAGES["SEVERAL_FREQUENCY_IN_THE_SAME_SHEET"]

    def __init__(self, email, id_dossier, file_name, sheet_name, frequencies):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.frequencies = frequencies

    def get_error_message(self):
        return self.MESSAGE.format(frequencies=self.frequencies)


class StartDateGreaterThanEndDateError(FileError):
    MESSAGE = MESSAGES["START_DATE_GREATER_THAN_END_DATE"]

    def __init__(self, email, id_dossier, file_name, sheet_name, start_date, end_date):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.start_date = start_date
        self.end_date = end_date

    def get_error_message(self):
        return self.MESSAGE.format(
            start_date=self.start_date.strftime("%Y-%m-%d"),
            end_date=self.end_date.strftime("%Y-%m-%d"),
        )


class DatesValuesAreNotIncludedInDateRangeError(FileError):
    MESSAGE = MESSAGES["DATES_VALUES_ARE_NOT_INCLUDED_IN_DATE_RANGE"]

    def __init__(
        self, email, id_dossier, file_name, start_date, end_date, dates, sheet_name
    ):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.start_date = start_date
        self.end_date = end_date
        self.dates = dates

    def get_error_message(self):
        return self.MESSAGE.format(
            start_date=self.start_date.strftime("%Y-%m-%d"),
            end_date=self.end_date.strftime("%Y-%m-%d"),
            dates=[d.strftime("%Y-%m-%d %H:%M") for d in self.dates],
        )


class ProfondeurNegatveError(FileError):
    MESSAGE = MESSAGES["PROFONDEUR_NEGATIVE"]

    def __init__(self, email, id_dossier, file_name, sheet_name, profondeur):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.profondeur = profondeur

    def get_error_message(self):
        return self.MESSAGE.format(profondeur=self.profondeur)


class ColonneHeureMalRemplieError(FileError):
    MESSAGE = MESSAGES["COLONNE_HEURE_MAL_REMPLIE"]

    def __init__(self, email, id_dossier, file_name, sheet_name, incorrect_value, row):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.incorrect_value = incorrect_value
        self.row = row

    def get_error_message(self):
        return self.MESSAGE.format(incorrect_value=self.incorrect_value, row=self.row)


class PHValueError(FileError):
    MESSAGE = MESSAGES["PH_VALUE_ERROR"]

    def __init__(self, email, id_dossier, file_name, sheet_name, incorrect_value, row):
        super().__init__(email, id_dossier, file_name, sheet_name)
        self.incorrect_value = incorrect_value
        self.row = row

    def get_error_message(self):
        return self.MESSAGE.format(incorrect_value=self.incorrect_value, row=self.row)
