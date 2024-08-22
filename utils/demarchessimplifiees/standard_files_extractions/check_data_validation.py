import datetime as dt

import numpy as np
import pandas as pd

from utils.common.exceptions import (
    AtLeastOneValueShouldBeProvidedByRowError,
    DateColumnContainsInvalidValuesError,
    DateFormatError,
    DatesValuesAreNotIncludedInDateRangeError,
    MissingDateError,
    ParameterIsMissingError,
    ProfondeurNegatveError,
    SeveralFrequencyInTheSameSheetError,
    StandardFileFileExtensionError,
    StandardFileFormatError,
    StandardFileParametersBadValueError,
    StandardFileParametersIsMissingError,
    StartDateGreaterThanEndDateError,
    TabsAreInvalidError,
    ValuesAreNotPositiveError,
)
from utils.common.utils import get_file_extension
from utils.demarchessimplifiees.common.constant import (
    STANDARD_V2_SHEETS_FREQUENCIES,
    TABLE_FILES_EXTENSIONS,
)


def check_file_extension(dossier, file):
    file_extension = get_file_extension(file.object_storage_key)
    if file_extension in TABLE_FILES_EXTENSIONS:
        return True
    raise StandardFileFileExtensionError(
        email=dossier.adresse_email_declarant,
        id_dossier=dossier.id_dossier,
        file_name=file.nom_fichier,
    )


def check_table_sheets_number(dossier, file, sheets, number):
    if len(sheets) == number:
        return True
    raise StandardFileFormatError(
        email=dossier.adresse_email_declarant,
        id_dossier=dossier.id_dossier,
        file_name=file.nom_fichier,
    )


def check_table_sheets(dossier, file, sheets, expected_sheets):
    if tuple(sheets.keys()) == expected_sheets:
        return True
    raise TabsAreInvalidError(
        email=dossier.adresse_email_declarant,
        id_dossier=dossier.id_dossier,
        file_name=file.nom_fichier,
        sheets=sheets.keys(),
        expected_sheets=expected_sheets,
    )


def valid_frequency_expected_values(sheet_name):
    if sheet_name == "Data_|_T=_autre":
        return True


def check_frequency(dossier, file, sheet_name, frequencies):
    if len(set(frequencies)) != 1:
        raise SeveralFrequencyInTheSameSheetError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
            sheet_name=sheet_name,
            frequencies=frequencies,
        )

    frequency = frequencies[0]

    if frequency not in STANDARD_V2_SHEETS_FREQUENCIES[sheet_name]:
        raise StandardFileParametersBadValueError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
            sheet_name=sheet_name,
            parameter_name="frequence",
            incorrect_value=frequency,
            expected_values=STANDARD_V2_SHEETS_FREQUENCIES[sheet_name],
        )


def check_validate_date_format(dossier, file, dates, sheet_name=None):
    for date in dates:
        if (not pd.isna(date)) or (not isinstance(date, dt.datetime)):
            raise DateColumnContainsInvalidValuesError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
            )


def check_values_are_positives(dossier, file, values, sheet_name=None):
    if np.any(values < 0):
        raise ValuesAreNotPositiveError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
            sheet_name=sheet_name,
        )


def check_value_present_per_row(
    dossier, file, tableur, sheet_name=None, remarques=None, start_row=3, start_column=1
):
    for row_id in range(len(tableur[start_row:, start_column:])):
        row = tableur[start_row:, start_column:][row_id]

        if np.all([isinstance(value, float) and np.isnan(value) for value in row]):
            if remarques is not None and pd.isna(remarques[row_id]):
                raise AtLeastOneValueShouldBeProvidedByRowError(
                    email=dossier.adresse_email_declarant,
                    id_dossier=dossier.id_dossier,
                    file_name=file.nom_fichier,
                    row=start_row + 1 + row_id,
                    sheet_name=sheet_name,
                )
            elif remarques is None:
                raise AtLeastOneValueShouldBeProvidedByRowError(
                    email=dossier.adresse_email_declarant,
                    id_dossier=dossier.id_dossier,
                    file_name=file.nom_fichier,
                    row=start_row + 1 + row_id,
                )


def check_date_is_not_missing(dossier, file, dates):
    for row_id in range(len(dates)):
        if pd.isna(dates[row_id]):
            raise MissingDateError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                row=4 + row_id,
            )
        if not isinstance(dates[row_id], dt.datetime):
            raise DateFormatError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                row=4 + row_id,
                current_value=dates[row_id],
            )


def check_parameter_is_not_provided(parameter):
    return (
        pd.isna(parameter) or parameter == "" or parameter is None or parameter == "nan"
    )


def check_parameters_present(
    dossier,
    file,
    parameter_name,
    parameter_type,
    parameter_frequency,
    parameter_unit,
    parameter_start_date,
    parameter_end_date,
):
    if (
        check_parameter_is_not_provided(parameter_name)
        or check_parameter_is_not_provided(parameter_type)
        or check_parameter_is_not_provided(parameter_frequency)
        or check_parameter_is_not_provided(parameter_unit)
        or check_parameter_is_not_provided(parameter_start_date)
        or check_parameter_is_not_provided(parameter_end_date)
    ):
        raise StandardFileParametersIsMissingError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
        )


def check_value_in_list(dossier, file, name, value, expected_values, sheet_name=None):
    if isinstance(value, float) and np.isnan(value):
        raise ParameterIsMissingError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
            sheet_name=sheet_name,
            parameter_name=name,
            expected_values=expected_values,
        )
    if value not in expected_values:
        raise StandardFileParametersBadValueError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
            sheet_name=sheet_name,
            parameter_name=name,
            incorrect_value=value,
            expected_values=expected_values,
        )


def check_values_in_list(dossier, file, name, values, expected_values, sheet_name=None):
    for value in values:
        check_value_in_list(dossier, file, name, value, expected_values, sheet_name)


def check_start_dates_and_end_dates(dossier, file, start_dates, end_dates, sheet_name):
    for start_date, end_date in zip(start_dates, end_dates):
        if (isinstance(start_date, float) and pd.isna(start_date)) or not isinstance(
            start_date, dt.datetime
        ):
            raise ParameterIsMissingError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
                parameter_name="date_debut",
                expected_values="une date au format aaaa-mm-jj",
            )
        if (isinstance(end_date, float) and pd.isna(end_date)) or not isinstance(
            end_date, dt.datetime
        ):
            raise ParameterIsMissingError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
                parameter_name="end_debut",
                expected_values="une date au format aaaa-mm-jj",
            )
        if not isinstance(start_date, dt.datetime):
            raise StandardFileParametersBadValueError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
                parameter_name="date_debut",
                incorrect_value=start_date,
                expected_values="une date au format aaaa-mm-jj",
            )
        if not isinstance(end_date, dt.datetime):
            raise StandardFileParametersBadValueError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
                parameter_name="date_fin",
                incorrect_value=end_date,
                expected_values="une date au format aaaa-mm-jj",
            )
        if start_date > end_date:
            raise StartDateGreaterThanEndDateError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
                start_date=start_date,
                end_date=end_date,
            )


def check_datetimes_are_included_in_start_dates_end_dates(
    dossier, file, start_dates, end_dates, datetimes, sheet_name
):
    for start_date, end_date in zip(start_dates, end_dates):
        current_datetimes = [
            current_datetime
            for current_datetime in datetimes
            if start_date > current_datetime or current_datetime > end_date
        ]
        if current_datetimes:
            raise DatesValuesAreNotIncludedInDateRangeError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
                start_date=start_date,
                end_date=end_date,
                dates=current_datetimes,
            )


def check_datetimes_are_not_null(dossier, file, datetimes, sheet_name):
    for i in range(len(datetimes)):
        if isinstance(datetimes[i], float) and np.isnan(datetimes[i]):
            raise MissingDateError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                row=13 + i,
                sheet_name=sheet_name,
            )


def check_profondeurs(dossier, file, depths, sheet_name):
    for depth in depths:
        if isinstance(depth, float) and np.isnan(depth):
            continue
        if depth < 0:
            raise ProfondeurNegatveError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
                profondeur=depth,
            )
