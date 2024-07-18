import datetime as dt
from collections import Counter
from io import BytesIO

import numpy as np
import pandas as pd
from sqlalchemy import select

from utils.common.exceptions import (
    DateColumnContainsDuplicateValuesError,
    DateColumnContainsInvalidValuesError,
    StandardFileFormatError,
    StandardFileParametersBadValueError,
)
from utils.common.logging import get_logger
from utils.common.object_storage_client import download_file
from utils.common.utils import get_file_extension
from utils.core.settings import settings
from utils.demarchessimplifiees.common.constant import (
    FREQUENCIES,
    STANDARD_V1_COLUMNS,
    STANDARD_V2_SHEETS,
    STANDARD_V2_SHEETS_FREQUENCIES,
    extract_file_engine,
)
from utils.demarchessimplifiees.data_extractions.models import (
    DonneesPointDePrelevement,
    PreprocessedDossier,
)
from utils.demarchessimplifiees.standard_files_extractions.check_data_validation import (
    check_file_extension,
    check_nom_point_de_prelevement,
    check_parameter_is_not_provided,
    check_table_sheets,
    check_table_sheets_number,
    check_value_present_per_row,
    check_values_are_positives,
)

logging = get_logger(__name__)


def get_donnees_point_de_prelevement_by_ddb_id(session, demarche_data_brute_id):
    query = select(DonneesPointDePrelevement).filter(
        DonneesPointDePrelevement.demarche_data_brute_id == demarche_data_brute_id
    )
    return session.execute(query).fetchall()


def get_preprocessed_dossier(session, demarche_data_brute_id, id_dossier):
    query = select(PreprocessedDossier).filter(
        PreprocessedDossier.demarche_data_brute_id == demarche_data_brute_id,
        PreprocessedDossier.id_dossier == id_dossier,
    )
    return session.execute(query).fetchone()


def convert_sheet_to_array(sheet):
    return np.vstack([sheet.columns.values, sheet.to_numpy()])


def string_to_timedelta(time_str):
    hours, minutes = map(int, time_str.split(":"))
    return dt.timedelta(hours=hours, minutes=minutes)


def process_standard_v1_file(dossier, file):
    file_extension = get_file_extension(file.object_storage_key)
    check_file_extension(dossier, file)

    downloaded_file = download_file(settings.SCW_S3_BUCKET, file.object_storage_key)
    with BytesIO(downloaded_file) as file_content:
        sheets = pd.read_excel(
            file_content,
            engine=extract_file_engine[file_extension],
            sheet_name=None,
        )

        check_table_sheets_number(dossier, file, sheets, 1)

        sheet = sheets[next(iter(sheets))]
        tableur = convert_sheet_to_array(sheet)
        columns = tuple(col.replace("\r", "").replace("\n", "") for col in tableur[2])

        dates = tableur[3:, 0]

        if columns != STANDARD_V1_COLUMNS:
            raise StandardFileFormatError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
            )

        if None in dates:
            raise DateColumnContainsInvalidValuesError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
            )

        # check_validate_date_format(dossier, file, dates)
        duplicated_dates = [date for date, count in Counter(dates).items() if count > 1]
        if duplicated_dates:
            raise DateColumnContainsDuplicateValuesError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                rows=duplicated_dates,
                sheet_name=None,
            )

        check_values_are_positives(dossier, file, tableur[3:, 1:].flatten())

        check_value_present_per_row(dossier, file, tableur)

        df_data = {
            "date_releve": [],
            "volume": [],
            "point_prelevement": [],
            "id_dossier": dossier.id_dossier,
            "demarche_data_brute_id": dossier.demarche_data_brute_id,
        }

        for col_id in range(1, len(tableur[0])):
            df_data["date_releve"].extend(dates)
            df_data["volume"].extend(tableur[3:, col_id])
            df_data["point_prelevement"].extend([columns[col_id]] * len(dates))
        df = pd.DataFrame(data=df_data)
        df = df[df.volume.notna()].reset_index(drop=True)
        return df


def generate_dates_array(start_date, end_date, frequency):
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += FREQUENCIES[frequency]
    return dates


def process_standard_v2_file(dossier, file):
    file_extension = get_file_extension(file.object_storage_key)

    check_file_extension(dossier, file)
    downloaded_file = download_file(settings.SCW_S3_BUCKET, file.object_storage_key)
    with BytesIO(downloaded_file) as file_content:
        sheets = pd.read_excel(
            file_content,
            engine=extract_file_engine[file_extension],
            sheet_name=None,
        )
        sheets = {key.replace(" ", "_"): value for key, value in sheets.items()}

        check_table_sheets_number(dossier, file, sheets, len(STANDARD_V2_SHEETS))
        check_table_sheets(dossier, file, sheets, STANDARD_V2_SHEETS)

        first_sheet = convert_sheet_to_array(sheets[STANDARD_V2_SHEETS[0]])

        common_data = check_nom_point_de_prelevement(dossier, first_sheet)

        common_data["id_dossier"] = dossier.id_dossier
        common_data["demarche_data_brute_id"] = dossier.demarche_data_brute_id
        list_df = []

        for curr_sheet_id in range(2, len(STANDARD_V2_SHEETS)):
            sheet_name = STANDARD_V2_SHEETS[curr_sheet_id]
            curr_sheet = convert_sheet_to_array(
                sheets[STANDARD_V2_SHEETS[curr_sheet_id]]
            )

            if len(curr_sheet[1:, 1]) <= 11:
                continue
            for i in range(2, len(curr_sheet[1, :])):

                parameter_name = curr_sheet[1, i]
                description_type = curr_sheet[2, i]
                frequency = curr_sheet[3, i]
                unit = curr_sheet[4, i]
                detail = curr_sheet[5, i]
                depth = curr_sheet[6, i]
                start_date = curr_sheet[7, i]
                end_date = curr_sheet[8, i]
                description_note = curr_sheet[9, i]

                dates = curr_sheet[12:, 0]
                heures = curr_sheet[12:, 1]
                # notes = curr_sheet[12:, -1]
                values = curr_sheet[12:, i]

                if check_parameter_is_not_provided(parameter_name):
                    continue
                else:

                    # check_parameters_are_present(dossier, file, parameter_name, parameter_type, parameter_frequency,
                    # parameter_unit, parameter_detail, parameter_depth, parameter_start_date, parameter_end_date)

                    if (STANDARD_V2_SHEETS_FREQUENCIES[sheet_name] != "autre") and (
                        STANDARD_V2_SHEETS_FREQUENCIES[sheet_name] != frequency
                    ):
                        raise StandardFileParametersBadValueError(
                            email=dossier.adresse_email_declarant,
                            id_dossier=dossier.id_dossier,
                            file_name=file.nom_fichier,
                            sheet_name=sheet_name,
                            parameter_name="frequence",
                        )

                    if start_date > end_date:
                        raise StandardFileParametersBadValueError(
                            email=dossier.adresse_email_declarant,
                            id_dossier=dossier.id_dossier,
                            file_name=file.nom_fichier,
                            sheet_name=sheet_name,
                            parameter_name="date_debut",
                        )

                    # if not check_parameter_is_not_provided(depth):
                    #    check_values_are_positives(dossier, file, [depth], sheet_name)

                    # check_validate_date_format(dossier, file, [start_date, end_date], sheet_name)
                    # check_validate_date_format(dossier, file, dates, sheet_name)
                    # check_value_in_list(dossier, file, "nom_parametre", parameter_name, PARAMETER_NAME_CHOOSES, sheet_name)
                    # check_value_in_list(dossier, file, "type", description_type, PARAMETER_TYPE_CHOOSES, sheet_name)
                    # check_value_in_list(dossier, file, "frequence", frequency, PARAMETER_FREQUENCY_CHOOSES, sheet_name)
                    # check_value_in_list(dossier, file, "unite", unit, PARAMETER_UNITE_CHOOSES, sheet_name)

                    # generated_dates = generate_dates_array(start_date, end_date, frequency)
                    # for provided_date, provided_hour, generated_date in zip(dates, heures, generated_dates):
                    # if provided_hour:
                    #    curr_date = provided_date + string_to_timedelta(provided_hour)
                    # if curr_date != generated_date:
                    #    raise DateColumnContainsInvalidValuesError(email=dossier.adresse_email_declarant,
                    #    id_dossier=dossier.id_dossier, file_name=file.nom_fichier, sheet_name=sheet_name, parameter_name="heure")

                    df = pd.DataFrame(
                        {
                            "date": dates,
                            "heure": heures,
                            "valeur": values,
                            "nom_parametre": parameter_name,
                            "type": description_type,
                            "frequence": frequency,
                            "unite": unit,
                            "detail_point_suivi": detail,
                            "profondeur": depth,
                            "date_debut": start_date,
                            "date_fin": end_date,
                            "remarque": description_note,
                        }
                        | common_data
                    )
                    list_df.append(df)
        return pd.concat(list_df, ignore_index=True)
