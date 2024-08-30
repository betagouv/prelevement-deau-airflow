import datetime as dt
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from utils.common.exceptions import (
    AtLeastOneValueShouldBeProvidedByRowError,
    DateFormatError,
    DatesValuesAreNotIncludedInDateRangeError,
    MissingDateError,
    ParameterIsMissingError,
    ProfondeurNegatveError,
    SeveralFrequencyInTheSameSheetError,
    StandardFileFileExtensionError,
    StandardFileFormatError,
    StandardFileParametersBadValueError,
    StartDateGreaterThanEndDateError,
    TabsAreInvalidError,
    ValuesAreNotPositiveError,
)
from utils.common.utils import get_file_extension
from utils.demarchessimplifiees.common.constant import (
    STANDARD_V2_SHEETS_FREQUENCIES,
    TABLE_FILES_EXTENSIONS,
)
from utils.demarchessimplifiees.data_extraction.models import Dossier
from utils.demarchessimplifiees.data_extraction.schemas import PieceJointeSerializer


def check_file_extension(dossier: Dossier, file: PieceJointeSerializer):
    file_extension = get_file_extension(file.object_storage)
    if file_extension in TABLE_FILES_EXTENSIONS:
        return True
    raise StandardFileFileExtensionError(
        email=dossier.adresse_email_declarant,
        id_dossier=dossier.id,
        file_name=file.filename,
    )


def check_table_sheets_number(
    dossier: Dossier,
    file: PieceJointeSerializer,
    sheets: dict[str, pd.DataFrame],
    sheets_tabs_number: int,
):
    if len(sheets) == sheets_tabs_number:
        return True
    raise StandardFileFormatError(
        email=dossier.adresse_email_declarant,
        id_dossier=dossier.id,
        file_name=file.filename,
    )


def check_table_sheets(
    dossier: Dossier,
    file: PieceJointeSerializer,
    sheets_tabs: Tuple,
    expected_sheets_tabs: Tuple[str],
):
    if sheets_tabs == expected_sheets_tabs:
        return True
    raise TabsAreInvalidError(
        email=dossier.adresse_email_declarant,
        id_dossier=dossier.id,
        file_name=file.filename,
        sheets=sheets_tabs,
        expected_sheets=expected_sheets_tabs,
    )


def check_frequencies(
    dossier: Dossier,
    file: PieceJointeSerializer,
    sheet_name: str,
    frequencies: List[str],
):
    if len(set(frequencies)) != 1:
        raise SeveralFrequencyInTheSameSheetError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id,
            file_name=file.filename,
            sheet_name=sheet_name,
            frequencies=frequencies,
        )

    frequency = frequencies[0]

    if frequency not in STANDARD_V2_SHEETS_FREQUENCIES[sheet_name]:
        raise StandardFileParametersBadValueError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id,
            file_name=file.filename,
            sheet_name=sheet_name,
            parameter_name="frequence",
            incorrect_value=frequency,
            expected_values=STANDARD_V2_SHEETS_FREQUENCIES[sheet_name],
        )


def check_values_are_positives(
    dossier: Dossier, file: PieceJointeSerializer, values: np.array, sheet_name=None
):
    if np.any(values < 0):
        raise ValuesAreNotPositiveError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id,
            file_name=file.filename,
            sheet_name=sheet_name,
        )


def check_value_present_per_row(
    dossier: Dossier,
    file: PieceJointeSerializer,
    tableur: np.array,
    start_row: int = 3,
    start_column: int = 1,
    sheet_name: Optional[str] = None,
    remarques: Optional[str] = None,
):
    for row_id in range(len(tableur[start_row:, start_column:])):
        row = tableur[start_row:, start_column:][row_id]

        if np.all([isinstance(value, float) and np.isnan(value) for value in row]):
            if remarques is not None and pd.isna(remarques[row_id]):
                raise AtLeastOneValueShouldBeProvidedByRowError(
                    email=dossier.adresse_email_declarant,
                    id_dossier=dossier.id,
                    file_name=file.filename,
                    row=start_row + 1 + row_id,
                    sheet_name=sheet_name,
                )
            elif remarques is None:
                raise AtLeastOneValueShouldBeProvidedByRowError(
                    email=dossier.adresse_email_declarant,
                    id_dossier=dossier.id,
                    file_name=file.filename,
                    row=start_row + 1 + row_id,
                )


def check_date_is_not_missing(dossier: Dossier, file: PieceJointeSerializer, dates):
    for row_id in range(len(dates)):
        if pd.isna(dates[row_id]):
            raise MissingDateError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                row=4 + row_id,
            )
        if not isinstance(dates[row_id], dt.datetime):
            raise DateFormatError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                row=4 + row_id,
                current_value=dates[row_id],
            )


def check_parameter_is_not_provided(parameter):
    return (
        pd.isna(parameter) or parameter == "" or parameter is None or parameter == "nan"
    )


def check_value_in_list(
    dossier: Dossier,
    file: PieceJointeSerializer,
    name,
    value,
    expected_values,
    sheet_name=None,
):
    if isinstance(value, float) and np.isnan(value):
        raise ParameterIsMissingError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id,
            file_name=file.filename,
            sheet_name=sheet_name,
            parameter_name=name,
            expected_values=expected_values,
        )
    if value not in expected_values:
        raise StandardFileParametersBadValueError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id,
            file_name=file.filename,
            sheet_name=sheet_name,
            parameter_name=name,
            incorrect_value=value,
            expected_values=expected_values,
        )


def check_values_in_list(
    dossier: Dossier,
    file: PieceJointeSerializer,
    name,
    values,
    expected_values,
    sheet_name=None,
):
    for value in values:
        check_value_in_list(dossier, file, name, value, expected_values, sheet_name)


def check_start_dates_and_end_dates(
    dossier,
    file: PieceJointeSerializer,
    start_dates: List,
    end_dates: List,
    sheet_name: str,
):
    for start_date, end_date in zip(start_dates, end_dates):
        if (isinstance(start_date, float) and pd.isna(start_date)) or not isinstance(
            start_date, dt.datetime
        ):
            raise ParameterIsMissingError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                sheet_name=sheet_name,
                parameter_name="date_debut",
                expected_values="une date au format aaaa-mm-jj",
            )
        if (isinstance(end_date, float) and pd.isna(end_date)) or not isinstance(
            end_date, dt.datetime
        ):
            raise ParameterIsMissingError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                sheet_name=sheet_name,
                parameter_name="end_debut",
                expected_values="une date au format aaaa-mm-jj",
            )
        if not isinstance(start_date, dt.datetime):
            raise StandardFileParametersBadValueError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                sheet_name=sheet_name,
                parameter_name="date_debut",
                incorrect_value=start_date,
                expected_values="une date au format aaaa-mm-jj",
            )
        if not isinstance(end_date, dt.datetime):
            raise StandardFileParametersBadValueError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                sheet_name=sheet_name,
                parameter_name="date_fin",
                incorrect_value=end_date,
                expected_values="une date au format aaaa-mm-jj",
            )
        if start_date > end_date:
            raise StartDateGreaterThanEndDateError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                sheet_name=sheet_name,
                start_date=start_date,
                end_date=end_date,
            )


def check_datetimes_are_included_in_start_dates_end_dates(
    dossier: Dossier,
    file: PieceJointeSerializer,
    start_dates: List,
    end_dates: List,
    datetimes: List,
    sheet_name: str,
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
                id_dossier=dossier.id,
                file_name=file.filename,
                sheet_name=sheet_name,
                start_date=start_date,
                end_date=end_date,
                dates=current_datetimes,
            )


def check_datetimes_are_not_null(
    dossier: Dossier,
    file: PieceJointeSerializer,
    datetimes: List[dt.datetime],
    sheet_name: str,
):
    for i in range(len(datetimes)):
        if isinstance(datetimes[i], float) and np.isnan(datetimes[i]):
            raise MissingDateError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                row=13 + i,
                sheet_name=sheet_name,
            )


def check_profondeurs(
    dossier: Dossier, file: PieceJointeSerializer, depths: List[float], sheet_name: str
):
    for depth in depths:
        if isinstance(depth, float) and np.isnan(depth):
            continue
        if depth < 0:
            raise ProfondeurNegatveError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                sheet_name=sheet_name,
                profondeur=depth,
            )
