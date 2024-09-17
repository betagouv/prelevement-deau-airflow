import datetime as dt
from io import BytesIO
from typing import List

import numpy as np
import pandas as pd
from sqlalchemy import and_, or_

from utils.common.exceptions import (
    ColonneHeureMalRemplieError,
    DateColumnContainsInvalidValuesError,
    DateColumnIsNotSortedError,
    FileError,
    PHValueError,
    StandardFileNomPointDePrelevementError,
    TableHeadersError,
    TableIsEmptyError,
)
from utils.common.logging import get_logger
from utils.common.messages import MESSAGES
from utils.common.object_storage_client import download_file
from utils.common.utils import encode64, get_file_extension
from utils.core.settings import settings
from utils.db.init_db import get_local_session
from utils.demarchessimplifiees.common.constant import (
    STANDARD_V1_COLUMNS,
    STANDARD_V2_SHEETS,
    extract_file_engine,
)
from utils.demarchessimplifiees.common.schemas import (
    CorrectionReasonEnum,
    ParametreEnum,
    TypeEnum,
    UniteEnum,
)
from utils.demarchessimplifiees.common.services import (
    changement_etat_dossier,
    dossier_envoyer_message,
)
from utils.demarchessimplifiees.data_extraction.models import (
    DonneesPointDePrelevementAPEZRE,
    DonneesPrelevementAEPZRE,
    DonneesPrelevementCiterne,
    Dossier,
    PrelevementCiterneValeurParValeur,
)
from utils.demarchessimplifiees.data_extraction.schemas import (
    DossierEtatEnum,
    DossierSousEtatEnum,
    PieceJointeSerializer,
    TypePrelevementEnum,
)
from utils.demarchessimplifiees.errors_management.models import ErrorMail
from utils.demarchessimplifiees.standard_files_extractions.check_data_validation import (
    check_date_is_not_missing,
    check_datetimes_are_included_in_start_dates_end_dates,
    check_datetimes_are_not_null,
    check_file_extension,
    check_frequencies,
    check_profondeurs,
    check_start_dates_and_end_dates,
    check_table_sheets,
    check_table_sheets_number,
    check_value_present_per_row,
    check_values_are_positives,
    check_values_in_list,
)

logging = get_logger(__name__)


def send_error_mail(dossier: Dossier, message: str, session):
    # TODO: Remove DEMARCHE_ID == 80149 FOR PRODUCTION
    if not settings.DRY_RUN or settings.DEMARCHE_ID == 80149:

        destination_dossier_id = encode64(f"Dossier-{dossier.id}")
        destination_dossier_token = settings.DEMARCHES_SIMPLIFIEES_TOKEN

        # TODO: Remove FOR PRODUCTION
        if settings.DEMARCHE_ID == 80149:
            destination_dossier_id = encode64(
                f"Dossier-{settings.TMP_ERROR_MESSAGE_RECEPTION_DOSSIER_ID}"
            )
            destination_dossier_token = (
                settings.TMP_ERROR_MESSAGE_RECEPTION_DEMARCHE_TOKEN
            )

        dossier_envoyer_message_result = dossier_envoyer_message(
            dossier_id=destination_dossier_id,
            instructeur_id=settings.INSTRUCTEUR_ID,
            body=MESSAGES["EMAIL_WRAPPER"].format(
                dossier_id=dossier.id,
                errors=message,
                instructeur_email=settings.INSTRUCTEUR_EMAIL,
                instructeur_telephone=settings.INSTRUCTEUR_TELEPHONE,
            ),
            correction=CorrectionReasonEnum.incorrect if not settings.DRY_RUN else None,
            token=destination_dossier_token,
        )
        if "errors" in dossier_envoyer_message_result:
            logging.error(
                f"[{dossier.id}] {dossier_envoyer_message_result['errors'][0]['message']}"
            )

    error_mail = ErrorMail(
        email=dossier.adresse_email_declarant,
        id_dossier=dossier.id,
        message=message,
    )
    session.add(error_mail)
    session.commit()
    logging.error(message)


def replace_nan_by_none(value):
    return None if isinstance(value, float) and pd.isna(value) else value


def download_excel(
    dossier: Dossier, file: PieceJointeSerializer
) -> dict[str, pd.DataFrame]:
    file_extension = get_file_extension(file.object_storage)
    check_file_extension(dossier, file)
    downloaded_file = download_file(settings.SCW_S3_BUCKET, file.object_storage)
    file_content = BytesIO(downloaded_file)
    sheets = pd.read_excel(
        file_content,
        engine=extract_file_engine[file_extension],
        sheet_name=None,
    )
    return sheets


def convert_sheet_to_array(sheet: pd.DataFrame) -> np.array:
    return np.vstack([sheet.columns.values, sheet.to_numpy()])


def sheet_is_empty(sheet: np.array) -> bool:
    return len(sheet[1:, 1]) <= 11


def remove_empty_columns(sheet: np.array) -> np.array:
    columns_to_keep = [0, 1]
    for i in range(2, 10):
        if not all(
            [isinstance(cell, float) and np.isnan(cell) for cell in sheet[12:, i]]
        ):
            columns_to_keep.append(i)
    return sheet[:, columns_to_keep]


def remove_empty_rows(sheet: np.array) -> np.array:
    rows_to_keep = [i for i in range(12)]
    for i in range(12, sheet.shape[0]):
        if not all(
            [isinstance(cell, float) and np.isnan(cell) for cell in sheet[i, :]]
        ):
            rows_to_keep.append(i)
    return sheet[rows_to_keep, :]


def get_first_sheet_data(
    dossier: Dossier, file: PieceJointeSerializer, sheet: np.array
) -> dict:
    if sheet.shape[1] != 2 or sheet[2, 1] == np.nan:
        raise StandardFileNomPointDePrelevementError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id,
            file_name=file.filename,
        )

    return {
        "nom_point_prelevement": sheet[2, 1],
        "nom_point_de_prelevement_associe": sheet[3, 1],
        "remarque_fonctionnement_point_de_prelevement": sheet[4, 1],
    }


def process_heures(
    dossier: Dossier, file: PieceJointeSerializer, sheet_name: str, heures: np.array
) -> list:
    processed_times = []

    for heure_id in range(len(heures)):
        current_heure = heures[heure_id]
        if isinstance(current_heure, str):
            parsed_time = dt.datetime.strptime(current_heure, "%H:%M").time()
            processed_times.append(parsed_time)
        elif isinstance(current_heure, dt.time):
            processed_times.append(current_heure)
        elif isinstance(current_heure, float) and np.isnan(current_heure):
            processed_times.append(current_heure)
        elif isinstance(current_heure, float) and not np.isnan(current_heure):
            raise ColonneHeureMalRemplieError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                sheet_name=sheet_name,
                incorrect_value=current_heure,
                row=heure_id + 13,
            )
        elif isinstance(current_heure, dt.datetime):
            processed_times.append(current_heure.time())
        else:
            raise ColonneHeureMalRemplieError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=file.filename,
                sheet_name=sheet_name,
                incorrect_value=current_heure,
                row=heure_id + 13,
            )

    return processed_times


def process_standard_citerne_file(
    dossier: Dossier, fichier_citerne: PieceJointeSerializer
) -> pd.DataFrame:
    sheets = download_excel(dossier, fichier_citerne)
    check_table_sheets_number(dossier, fichier_citerne, sheets, 1)

    sheet = sheets[next(iter(sheets))]
    tableur: np.array = convert_sheet_to_array(sheet)
    headers = tuple(col.replace("\r", "").replace("\n", "") for col in tableur[2])

    dates = tableur[3:, 0]

    if headers != STANDARD_V1_COLUMNS:
        raise TableHeadersError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id,
            file_name=fichier_citerne.filename,
            sheet_name=None,
            headers=headers,
            expected_headers=STANDARD_V1_COLUMNS,
        )
    if None in dates:
        raise DateColumnContainsInvalidValuesError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id,
            file_name=fichier_citerne.filename,
        )

    check_date_is_not_missing(dossier, fichier_citerne, dates)

    for i in range(len(dates) - 1):
        if dates[i] >= dates[i + 1]:
            raise DateColumnIsNotSortedError(
                email=dossier.adresse_email_declarant,
                id_dossier=dossier.id,
                file_name=fichier_citerne.filename,
                row1=i + 4,
                row2=i + 5,
                sheet_name=None,
            )

    check_value_present_per_row(dossier, fichier_citerne, tableur)
    check_values_are_positives(dossier, fichier_citerne, tableur[3:, 1:].flatten())

    df_data = {
        "date_releve": [],
        "volume": [],
        "nom_point_prelevement": [],
        "id_dossier": dossier.id,
    }

    for col_id in range(1, len(tableur[0])):
        df_data["date_releve"].extend(dates)
        df_data["volume"].extend(tableur[3:, col_id])
        df_data["nom_point_prelevement"].extend([headers[col_id]] * len(dates))
    df = pd.DataFrame(data=df_data)
    df = df[df.volume.notna()].reset_index(drop=True)
    if df.empty:
        raise TableIsEmptyError(
            email=dossier.adresse_email_declarant,
            id_dossier=dossier.id,
            file_name=fichier_citerne.filename,
        )
    return df


def process_aep_or_zre_file(
    dossier: Dossier,
    donnee_point_de_prelevement: DonneesPointDePrelevementAPEZRE,
    file: PieceJointeSerializer,
):
    file_data = []
    sheets = download_excel(dossier, file)
    sheets = {key.replace(" ", "_"): value for key, value in sheets.items()}

    check_table_sheets_number(dossier, file, sheets, len(STANDARD_V2_SHEETS))
    check_table_sheets(dossier, file, tuple(sheets.keys()), STANDARD_V2_SHEETS)
    first_sheet = convert_sheet_to_array(sheets[STANDARD_V2_SHEETS[0]])
    common_data = get_first_sheet_data(dossier, file, first_sheet)
    common_data["id_dossier"] = dossier.id

    for current_sheet_id in range(2, len(STANDARD_V2_SHEETS)):
        sheet_name = STANDARD_V2_SHEETS[current_sheet_id]
        current_sheet = convert_sheet_to_array(
            sheets[STANDARD_V2_SHEETS[current_sheet_id]]
        )

        if sheet_is_empty(current_sheet):
            continue
        current_sheet = remove_empty_columns(current_sheet)
        current_sheet = remove_empty_rows(current_sheet)

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
        check_frequencies(dossier, file, sheet_name, frequencies)
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
        datetimes: List[dt.datetime] = [
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
            dossier=dossier,
            file=file,
            tableur=current_sheet,
            sheet_name=sheet_name,
            remarques=values_remarques,
            start_row=12,
            start_column=1,
        )
        for column_id in range(2, current_sheet.shape[1]):
            for row_id in range(12, current_sheet.shape[0] - 1):

                if ParametreEnum(parameter_names[column_id - 2]) == ParametreEnum.PH:
                    if (
                        current_sheet[row_id, column_id] < 0
                        or current_sheet[row_id, column_id] > 14
                    ):
                        raise PHValueError(
                            email=dossier.adresse_email_declarant,
                            id_dossier=dossier.id,
                            file_name=file.filename,
                            sheet_name=sheet_name,
                            incorrect_value=current_sheet[row_id, column_id],
                            row=row_id + 1,
                        )
                file_data.append(
                    {
                        "donnees_point_de_prelevement_aep_zre_id": donnee_point_de_prelevement.id,
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


def accepte_dossier_if_not_accepted(dossier: Dossier):
    # TODO: Remove FOR PRODUCTION
    if (
        (DossierEtatEnum(dossier.etat_dossier) == DossierEtatEnum.EN_INSTRUCTION)
        and (not settings.DRY_RUN)
        and (settings.DEMARCHE_ID != 80149)
    ):
        dossier_accepter_result = changement_etat_dossier(
            dossier_id=encode64(f"Dossier-{dossier.id}"),
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
            logging.error(f"[{dossier.id}] {dossier_accepter_result_errors}")
        logging.info(f"[{dossier.id}] Dossier accepté")


def collect_citerne_data():
    with get_local_session() as session:
        query_dossiers_fichier_citerne = (
            session.query(Dossier)
            .filter(
                Dossier.type_prelevement
                == TypePrelevementEnum.PRELEVEMENT_CAMION_CITERNE
            )
            .filter(
                or_(
                    Dossier.etat_dossier.in_(
                        [DossierEtatEnum.EN_INSTRUCTION, DossierEtatEnum.ACCEPTE]
                    ),
                    and_(
                        Dossier.etat_dossier == DossierEtatEnum.EN_CONSTRUCTION,
                        Dossier.sous_etat_dossier == DossierSousEtatEnum.CORRIGE,
                    ),
                ),
                Dossier.fichier_tableau_suivi_camion_citerne_object_storage.isnot(None),
            )
        )

    for dossier in query_dossiers_fichier_citerne:
        fichier_citerne = PieceJointeSerializer.model_validate(
            {
                "filename": dossier.fichier_tableau_suivi_camion_citerne_filename,
                "url": dossier.fichier_tableau_suivi_camion_citerne_url,
                "object_storage": dossier.fichier_tableau_suivi_camion_citerne_object_storage,
            }
        )
        try:
            data = process_standard_citerne_file(dossier, fichier_citerne)
            donnees_prelevement_citerne = data.apply(
                lambda x: DonneesPrelevementCiterne(**x), axis=1
            )
            session.add_all(donnees_prelevement_citerne)
            accepte_dossier_if_not_accepted(dossier)
            session.commit()
        except FileError as e:
            send_error_mail(dossier, e.get_message_to_send(), session)
            logging.error(f"[{dossier.id}] FileError : {e}")
        except Exception as e:
            logging.error(f"Error processing dossier {dossier.id}: {e}")


def collect_prelevement_aep_zre():
    with get_local_session() as session:
        query_dossiers_ape_zre = session.query(Dossier).filter(
            and_(
                Dossier.type_prelevement == TypePrelevementEnum.PRELEVEMENT_APE_ZRE,
                or_(
                    Dossier.etat_dossier.in_(
                        [DossierEtatEnum.EN_INSTRUCTION, DossierEtatEnum.ACCEPTE]
                    ),
                    and_(
                        Dossier.etat_dossier == DossierEtatEnum.EN_CONSTRUCTION,
                        Dossier.sous_etat_dossier == DossierSousEtatEnum.CORRIGE,
                    ),
                ),
            )
        )

        # Parcourir les dossiers
        for dossier in query_dossiers_ape_zre:
            dossier_data = []
            dossier_errors = []

            dossier_donnees_point_de_prelevement_aep_zre: List[
                DonneesPointDePrelevementAPEZRE
            ] = dossier.donnees_point_de_prelevement_aep_zre
            for (
                donnee_point_de_prelevement
            ) in dossier_donnees_point_de_prelevement_aep_zre:
                try:
                    fichier_citerne = PieceJointeSerializer.model_validate(
                        {
                            "filename": donnee_point_de_prelevement.fichier_prelevement_filename,
                            "url": donnee_point_de_prelevement.fichier_prelevement_url,
                            "object_storage": donnee_point_de_prelevement.fichier_prelevement_object_storage,
                        }
                    )
                    data = process_aep_or_zre_file(
                        dossier, donnee_point_de_prelevement, fichier_citerne
                    )
                    dossier_data += data
                except FileError as e:
                    dossier_errors.append(e.get_message_to_send())
                    logging.error(f"[{dossier.id}] FileError : {e}")
                except Exception as e:
                    logging.error(f"[{dossier.id}] exception : {e}")

            if dossier_errors:
                send_error_mail(dossier, "- " + "\n- ".join(dossier_errors), session)
            else:
                donnees_prelevement_aep_zre = [
                    DonneesPrelevementAEPZRE(
                        donnees_point_de_prelevement_aep_zre_id=donnee_point_de_prelevement.id,
                        date=x.get("date"),
                        valeur=x.get("valeur"),
                        nom_parametre=x.get("nom_parametre"),
                        type=x.get("type"),
                        frequence=x.get("frequence"),
                        unite=x.get("unite"),
                        detail_point_suivi=replace_nan_by_none(
                            x.get("detail_point_suivi")
                        ),
                        remarque_serie_donnees=replace_nan_by_none(
                            x.get("remarque_serie_donnees")
                        ),
                        remarque=replace_nan_by_none(x.get("remarque")),
                        profondeur=replace_nan_by_none(x.get("profondeur")),
                        date_debut=x.get("date_debut"),
                        date_fin=x.get("date_fin"),
                        nom_point_prelevement=x.get("nom_point_prelevement"),
                        nom_point_de_prelevement_associe=replace_nan_by_none(
                            x.get("nom_point_de_prelevement_associe")
                        ),
                        remarque_fonctionnement_point_de_prelevement=replace_nan_by_none(
                            x.get("remarque_fonctionnement_point_de_prelevement")
                        ),
                    )
                    for x in dossier_data
                ]
                session.add_all(donnees_prelevement_aep_zre)
                session.commit()
                accepte_dossier_if_not_accepted(dossier)


def changement_etat_prelevement_autre_type():
    with get_local_session() as session:
        query_dossiers_autre_prelevement = session.query(Dossier).filter(
            Dossier.type_prelevement == TypePrelevementEnum.PRELEVEMENT_AUTRE,
            Dossier.etat_dossier.in_([DossierEtatEnum.EN_INSTRUCTION]),
        )

        for dossier in query_dossiers_autre_prelevement:
            accepte_dossier_if_not_accepted(dossier)


def changement_etat_citerne_valeur_par_valeur():
    with get_local_session() as session:
        query_dossiers_citerne_valeur_par_valeur = session.query(Dossier).where(
            Dossier.id.in_(
                session.query(
                    PrelevementCiterneValeurParValeur.id_dossier
                ).scalar_subquery()
            )
        )

        for dossier in query_dossiers_citerne_valeur_par_valeur:
            if Dossier.prelevements_citerne_valeur_par_valeur:
                accepte_dossier_if_not_accepted(dossier)
