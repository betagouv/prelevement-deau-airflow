import datetime as dt
from collections import Counter
from io import BytesIO

import numpy as np
import pandas as pd
from sqlalchemy import select

from utils.common.exceptions import (
    ColonneHeureMalRemplieError,
    DateColumnContainsDuplicateValuesError,
    DateColumnContainsInvalidValuesError,
    StandardFileNomPointDePrelevementError,
    TableHeadersError,
    TableIsEmptyError,
)
from utils.common.logging import get_logger
from utils.common.object_storage_client import download_file
from utils.common.utils import encode64, get_file_extension
from utils.core.settings import settings
from utils.demarchessimplifiees.common.constant import (
    FREQUENCIES,
    STANDARD_V1_COLUMNS,
    STANDARD_V2_SHEETS,
    extract_file_engine,
)
from utils.demarchessimplifiees.common.models import ParametreEnum, TypeEnum, UniteEnum
from utils.demarchessimplifiees.common.schemas import CorrectionReasonEnum, DossierState
from utils.demarchessimplifiees.data_extractions.models import (
    DonneesPointDePrelevement,
    PreprocessedDossier,
)
from utils.demarchessimplifiees.data_extractions.services import (
    changement_etat_dossier,
    dossier_envoyer_message,
)
from utils.demarchessimplifiees.errors_management.models import ErrorMail
from utils.demarchessimplifiees.standard_files_extractions.check_data_validation import (
    check_date_is_not_missing,
    check_datetimes_are_included_in_start_dates_end_dates,
    check_datetimes_are_not_null,
    check_file_extension,
    check_frequency,
    check_profondeurs,
    check_start_dates_and_end_dates,
    check_table_sheets,
    check_table_sheets_number,
    check_value_present_per_row,
    check_values_are_positives,
    check_values_in_list,
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


def generate_dates_array(start_date, end_date, frequency):
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += FREQUENCIES[frequency]
    return dates


def download_excel(dossier, file):
    file_extension = get_file_extension(file.object_storage_key)
    check_file_extension(dossier, file)
    if file_extension not in extract_file_engine:
        raise ValueError(f"Unsupported file extension: {file_extension}")
    downloaded_file = download_file(settings.SCW_S3_BUCKET, file.object_storage_key)
    file_content = BytesIO(downloaded_file)
    sheets = pd.read_excel(
        file_content,
        engine=extract_file_engine[file_extension],
        sheet_name=None,
    )
    return sheets


def replace_nan_by_none(value):
    return None if isinstance(value, float) and pd.isna(value) else value


def get_first_sheet_data(dossier, file, sheet):
    if sheet.shape[1] != 2 or sheet[2, 1] == np.nan:
        raise StandardFileNomPointDePrelevementError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
        )

    return {
        "nom_point_prelevement": sheet[2, 1],
        "nom_point_de_prelevement_associe": sheet[3, 1],
        "remarque_fonctionnement_point_de_prelevement": sheet[4, 1],
    }


def sheet_is_empty(sheet):
    return len(sheet[1:, 1]) <= 11


def remove_empty_columns(array):
    nb_columns = array.shape[1]

    columns_to_keep = [0, 1]

    for i in range(2, nb_columns):
        if not all(
            [isinstance(cell, float) and np.isnan(cell) for cell in array[12:, i]]
        ):
            columns_to_keep.append(i)

    return array[:, columns_to_keep]


def process_heures(dossier, file, sheet_name, elements):
    processed_times = []

    for element_id in range(len(elements)):
        element = elements[element_id]
        if isinstance(element, str):
            parsed_time = dt.datetime.strptime(element, "%H:%M").time()
            processed_times.append(parsed_time)
        elif isinstance(element, dt.time):
            processed_times.append(element)
        elif isinstance(element, float) and np.isnan(element):
            processed_times.append(element)
        elif isinstance(element, float) and not np.isnan(element):
            raise ColonneHeureMalRemplieError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
                incorrect_value=element,
                row=element_id + 13,
            )
        elif isinstance(element, dt.datetime):
            processed_times.append(element.time())
        else:
            raise ColonneHeureMalRemplieError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id_dossier,
                file_name=file.nom_fichier,
                sheet_name=sheet_name,
                incorrect_value=element,
                row=element_id + 13,
            )

    return processed_times


def process_standard_citerne_file(dossier, file):
    sheets = download_excel(dossier, file)

    check_table_sheets_number(dossier, file, sheets, 1)

    sheet = sheets[next(iter(sheets))]
    tableur = convert_sheet_to_array(sheet)
    headers = tuple(col.replace("\r", "").replace("\n", "") for col in tableur[2])

    dates = tableur[3:, 0]

    if headers != STANDARD_V1_COLUMNS:
        raise TableHeadersError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
            sheet_name=None,
            headers=headers,
            expected_headers=STANDARD_V1_COLUMNS,
        )

    if None in dates:
        raise DateColumnContainsInvalidValuesError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
        )

    check_date_is_not_missing(dossier, file, dates)
    duplicated_dates = [date for date, count in Counter(dates).items() if count > 1]
    if duplicated_dates:
        raise DateColumnContainsDuplicateValuesError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
            duplicated_dates=duplicated_dates,
            sheet_name=None,
        )

    check_value_present_per_row(dossier, file, tableur)
    check_values_are_positives(dossier, file, tableur[3:, 1:].flatten())

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
        df_data["point_prelevement"].extend([headers[col_id]] * len(dates))
    df = pd.DataFrame(data=df_data)
    df = df[df.volume.notna()].reset_index(drop=True)
    if df.empty:
        raise TableIsEmptyError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id_dossier,
            file_name=file.nom_fichier,
        )
    return df


def process_aep_or_zre_file(donnees_point_de_prelevement, dossier, file):
    file_data = []

    sheets = download_excel(donnees_point_de_prelevement.id_dossier, file)
    sheets = {key.replace(" ", "_"): value for key, value in sheets.items()}

    check_table_sheets_number(dossier, file, sheets, len(STANDARD_V2_SHEETS))
    check_table_sheets(dossier, file, sheets, STANDARD_V2_SHEETS)
    first_sheet = convert_sheet_to_array(sheets[STANDARD_V2_SHEETS[0]])
    common_data = get_first_sheet_data(dossier, file, first_sheet)
    common_data["id_dossier"] = dossier.id_dossier
    common_data["demarche_data_brute_id"] = dossier.demarche_data_brute_id

    for current_sheet_id in range(2, len(STANDARD_V2_SHEETS)):
        sheet_name = STANDARD_V2_SHEETS[current_sheet_id]
        current_sheet = convert_sheet_to_array(
            sheets[STANDARD_V2_SHEETS[current_sheet_id]]
        )

        if sheet_is_empty(current_sheet):
            continue

        current_sheet = remove_empty_columns(current_sheet)

        values_remarques = [None for _ in range(current_sheet.shape[0] - 12)]
        if current_sheet[11, -1] == "remarque":
            values_remarques = current_sheet[12:, -1]
            current_sheet = current_sheet[:, :-1]

        parameter_names = current_sheet[1, 2:]
        description_types = current_sheet[2, 2:]
        frequencies = current_sheet[3, 2:]
        units = current_sheet[4, 2:]
        details = current_sheet[5, 2:]
        depths = current_sheet[6, 2:]
        start_dates = current_sheet[7, 2:]
        end_dates = current_sheet[8, 2:]
        description_serie_donnees_remarque = current_sheet[9, 2:]

        current_sheet_dates = current_sheet[12:, 0]
        current_sheet_heures = current_sheet[12:, 1]
        current_sheet_heures = process_heures(
            dossier, file, sheet_name, current_sheet_heures
        )

        # Check parameters
        check_frequency(dossier, file, sheet_name, frequencies)
        frequency = frequencies[0]

        check_values_in_list(
            dossier,
            file,
            "parameter_name",
            parameter_names,
            ParametreEnum._value2member_map_.keys(),
            sheet_name,
        )
        check_values_in_list(
            dossier,
            file,
            "type",
            description_types,
            TypeEnum._value2member_map_.keys(),
            sheet_name,
        )
        check_values_in_list(
            dossier,
            file,
            "unite",
            units,
            UniteEnum._value2member_map_.keys(),
            sheet_name,
        )
        check_profondeurs(dossier, file, depths, sheet_name)

        check_start_dates_and_end_dates(
            dossier, file, start_dates, end_dates, sheet_name
        )
        start_dates = [
            start_date.replace(hour=0, minute=0) for start_date in start_dates
        ]
        end_dates = [end_date.replace(hour=23, minute=59) for end_date in end_dates]

        datetimes = [
            (
                dt.datetime.combine(date.date(), t)
                if not (isinstance(t, float) and np.isnan(t))
                else date
            )
            for date, t in zip(current_sheet_dates, current_sheet_heures)
        ]

        check_datetimes_are_not_null(dossier, file, datetimes, sheet_name)

        check_datetimes_are_included_in_start_dates_end_dates(
            dossier, file, start_dates, end_dates, datetimes, sheet_name
        )

        check_value_present_per_row(
            dossier,
            file,
            current_sheet,
            sheet_name,
            remarques=values_remarques,
            start_row=12,
            start_column=1,
        )

        for column_id in range(2, current_sheet.shape[1]):
            for row_id in range(12, current_sheet.shape[0] - 1):
                file_data.append(
                    {
                        "nom_parametre": parameter_names[column_id - 2],
                        "type": description_types[column_id - 2],
                        "frequence": frequency,
                        "unite": units[column_id - 2],
                        "profondeur": depths[column_id - 2],
                        "date_debut": start_dates[column_id - 2],
                        "date_fin": end_dates[column_id - 2],
                        "date": datetimes[row_id - 12],
                        "valeur": current_sheet[row_id, column_id],
                        "detail_point_suivi": details[column_id - 2],
                        "remarque_serie_donnees": description_serie_donnees_remarque[
                            column_id - 2
                        ],
                        "remarque": values_remarques[row_id - 12],
                        **common_data,
                    }
                )
        return file_data


def accepte_dossier_if_not_accepted(dossier):
    if (
        (DossierState(dossier.etat_dossier) == DossierState.EN_INSTRUCTION)
        and (not settings.DRY_RUN)
        and (settings.DEMARCHE_ID != 80149)
    ):
        dossier_accepter_result = changement_etat_dossier(
            dossier_id=encode64(f"Dossier-{dossier.id_dossier}"),
            instructeur_id=settings.INSTRUCTEUR_ID,
            operation="dossierAccepter",
        )
        if dossier_accepter_result["data"]["dossierAccepter"]["errors"]:
            dossier_accepter_result_errors = ". ".join(
                [
                    f"{error['message']}"
                    for error in dossier_accepter_result["data"]["dossierAccepter"][
                        "errors"
                    ]
                ]
            )
            logging.error(f"[{dossier.id_dossier}] {dossier_accepter_result_errors}")
        logging.info(f"[{dossier.id_dossier}] Dossier accepté")


def send_error_mail(dossier, message, demarche_data_brute_id, session):
    if (not settings.DRY_RUN) and (settings.DEMARCHE_ID != 80149):
        dossier_envoyer_message_result = dossier_envoyer_message(
            dossier_id=encode64(f"Dossier-{dossier.id_dossier}"),
            instructeur_id=settings.INSTRUCTEUR_ID,
            body=message,
            correction=CorrectionReasonEnum.incorrect,
        )
        if dossier_envoyer_message_result["data"]["dossierEnvoyerMessage"]["errors"]:
            dossier_envoyer_message_result_errors = ". ".join(
                [
                    f"{error['message']}"
                    for error in dossier_envoyer_message_result["data"][
                        "dossierEnvoyerMessage"
                    ]["errors"]
                ]
            )
            logging.error(
                f"[{dossier.id_dossier}] {dossier_envoyer_message_result_errors}"
            )
    error_mail = ErrorMail(
        demarche_data_brute_id=demarche_data_brute_id,
        email=dossier.adresse_email_declarant,
        id_dossier=dossier.id_dossier,
        message=message,
    )
    session.add(error_mail)
    session.commit()
    logging.error(message)
