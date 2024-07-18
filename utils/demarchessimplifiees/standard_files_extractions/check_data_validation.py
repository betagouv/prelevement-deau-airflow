import datetime as dt

import numpy as np
import pandas as pd

from utils.common.exceptions import (
    AtLeastOneValueShouldBeProvidedByRowError,
    DateColumnContainsInvalidValuesError,
    StandardFileFileExtensionError,
    StandardFileFormatError,
    StandardFileNomPointDePrelevementError,
    StandardFileParametersBadValueError,
    StandardFileParametersIsMissingError,
    ValuesAreNotPositiveError,
)
from utils.common.utils import get_file_extension
from utils.demarchessimplifiees.common.constant import TABLE_FILES_EXTENSIONS


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
    raise StandardFileFormatError(
        email=dossier.adresse_email_declarant,
        id_dossier=dossier.id_dossier,
        file_name=file.nom_fichier,
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


def check_value_present_per_row(dossier, file, tableur):
    for row in tableur[3:, 1:]:
        if np.all([np.isnan(value) for value in row]):
            raise AtLeastOneValueShouldBeProvidedByRowError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                row=3 + row,
            )


def check_nom_point_de_prelevement(dossier, sheet):
    if sheet[2, 1] == np.nan:
        raise StandardFileNomPointDePrelevementError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=dossier.nom_fichier,
        )

    return {
        "nom_point_prelevement": sheet[2, 1],
        "nom_point_de_prelevement_associe": sheet[3, 1],
        "remarque_fonctionnement_point_de_prelevement": sheet[4, 1],
    }


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


def check_value_in_list(dossier, file, name, value, list_chooses, sheet_name=None):
    if value not in list_chooses:
        raise StandardFileParametersBadValueError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
            sheet_name=sheet_name,
            parameter_name=name,
        )
