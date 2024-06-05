import copy
import datetime
import os
import uuid
from io import BytesIO
from typing import List

import numpy as np
import pandas as pd
import requests
from sqlalchemy import select

from utils.common.object_storage_client import download_file, upload_file
from utils.common.utils import decode64, get_file_extension
from utils.core.settings import settings
from utils.core.tools import open_file, write_file
from utils.demarchessimplifiees.constant import (
    champs_checkbox_db_labels,
    champs_date_db_labels,
    champs_integer_number_db_labels,
    champs_repetition_db_labels,
    champs_text_db_labels,
    extract_file_engine,
    tuple_fichier_standard_v2_onglets,
)
from utils.demarchessimplifiees.models import (
    DonneesPointDePrelevement,
    PreprocessedDossier,
)
from utils.demarchessimplifiees.schemas import (
    Champ,
    ChampType,
    CheckboxChamp,
    DateChamp,
    DecimalNumberChamp,
    Demarche,
    DonneesPointDePrelevementSerializer,
    Dossier,
    EnrichedAvisSerializer,
    EnrichedFileSerializer,
    EnrichedMessageSerializer,
    ExtraitDeRegistreSerializer,
    IntegerNumberChamp,
    ListFiles,
    MultipleDropDownListChamp,
    PieceJustificativeChamp,
    PreprocessedDossierSerializer,
    ReleveIndexSerializer,
    RepetitionChamp,
    TextChamp,
    VolumesPompesSerializer,
)


def get_demarche_from_demarches_simplifiees(demarche_number: int) -> str:
    query = open_file(
        path=os.path.join(
            os.getenv("AIRFLOW_HOME"),
            "utils/demarchessimplifiees/gql_queries/get_queries.gql",
        )
    )
    response = requests.post(
        url=settings.DEMARCHES_SIMPLIFIEES_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.DEMARCHES_SIMPLIFIEES_TOKEN}",
        },
        json={
            "query": query,
            "variables": {
                "demarcheNumber": demarche_number,
                "includeDossiers": True,
                "includeAvis": True,
                "includeMessages": True,
            },
            "operationName": "getDemarche",
        },
    )
    return response.content.decode("utf-8")


def save_demarche_to_file(demarche_number: int, demarche: str, hashed_data: str) -> str:
    file_path = os.path.join(
        os.getenv("AIRFLOW_HOME"),
        f"data/demandes_simplifiees/demarches_donnees_brutes/demarche__{demarche_number}__{hashed_data}.json",
    )
    write_file(path=file_path, content=demarche)
    return file_path


def process_piece_justificative(
    piece_justificative: PieceJustificativeChamp | ListFiles,
    prefix_object_storage_key: str,
) -> List[EnrichedFileSerializer]:
    files = []
    for pj in piece_justificative.files:
        id = uuid.uuid4()
        new_file = EnrichedFileSerializer.validate(
            {
                "id": str(id),
                "checksum": pj.checksum,
                "type_fichier": pj.contentType,
                "nom_fichier": pj.filename,
                "demarches_simplifiees_url": pj.url,
                "object_storage_key": f"{prefix_object_storage_key}{id}__{pj.filename}",
            }
        )
        response = requests.get(pj.url)
        upload_file(
            settings.SCW_S3_BUCKET,
            new_file.object_storage_key,
            response.content,
            acl="bucket-owner-read",
        )
        files.append(new_file)
    return files


def champ_to_pytandic(champ: dict):
    if "__typename" not in champ:
        raise Exception("PAS UN CHAMP")
    champ["champType"] = champ["__typename"]
    if champ["__typename"] == ChampType.CHECKBOX.value:
        return CheckboxChamp.validate(champ)
    elif champ["__typename"] == ChampType.DATE.value:
        return DateChamp.validate(champ)
    elif champ["__typename"] == ChampType.INTEGER_NUMBER.value:
        return IntegerNumberChamp.validate(champ)
    elif champ["__typename"] == ChampType.TEXT.value:
        return TextChamp.validate(champ)
    elif champ["__typename"] == ChampType.PIECE_JUSTIFICATIVE.value:
        return PieceJustificativeChamp.validate(champ)
    elif champ["__typename"] == ChampType.DECIMAL_NUMBER.value:
        return DecimalNumberChamp.validate(champ)
    elif champ["__typename"] == ChampType.MULTIPLE_DROPDOWN_LIST.value:
        return MultipleDropDownListChamp.validate(champ)
    elif champ["__typename"] == ChampType.REPETITION.value:
        if champ["rows"]:
            nb_rows = len(champ["rows"])
            for r_id in range(nb_rows):
                champ["rows"][r_id]["champs"] = champs_to_pydantic(
                    champ["rows"][r_id]["champs"]
                )
        return RepetitionChamp.validate(champ)
    else:
        raise Exception(f"le typename non connu: {champ['__typename']}")


def champs_to_pydantic(champs: List[dict]):
    processed_champs: List[Champ] = []
    for champ in champs:
        processed_champs.append(champ_to_pytandic(champ))
    return processed_champs


def get_demarche(demarches_simplfiees_data: dict):
    current_demarche_dict = copy.deepcopy(demarches_simplfiees_data)
    for n_id in range(
        len(current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"])
    ):
        current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"][n_id][
            "champs"
        ] = champs_to_pydantic(
            current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"][n_id][
                "champs"
            ]
        )
    current_demarche = Demarche.validate(current_demarche_dict["data"]["demarche"])
    return current_demarche


def process_dossier(current_dossier: Dossier) -> PreprocessedDossierSerializer:
    now = datetime.datetime.now()
    data = {}
    # ID
    data["id_dossier"] = current_dossier.number
    # Email
    data["adresse_email_connexion"] = current_dossier.usager.email
    # Civilité
    data["civilite_declarant"] = current_dossier.demandeur.civilite
    # Nom
    data["nom_declarant"] = current_dossier.demandeur.nom
    # Prénom
    data["prenom_declarant"] = current_dossier.demandeur.prenom
    # Dépôt pour un tiers
    data["depot_pour_mandataire"] = current_dossier.deposeParUnTiers
    # Nom du mandataire
    data["nom_mandataire"] = current_dossier.nomMandataire
    # Prénom du mandataire
    data["prenom_mandataire"] = current_dossier.prenomMandataire
    # Archivé
    data["archive"] = current_dossier.archived
    # État du dossier
    data["etat_dossier"] = current_dossier.state
    # Dernière mise à jour le
    data["derniere_mise_a_jour"] = current_dossier.dateDerniereModification
    # Déposé le
    data["date_depot"] = current_dossier.dateDepot
    # Passé en instruction le
    data["date_passage_instruction"] = current_dossier.datePassageEnInstruction
    # Traité le
    data["date_traitement"] = current_dossier.dateTraitement
    # Motivation de la décision
    data["motivation_decision"] = current_dossier.motivation
    # Instructeurs
    data["instructeurs"] = current_dossier.instructeurs
    # groupe instructeur
    data["groupe_instructeur"] = current_dossier.groupeInstructeur.label

    for champ in current_dossier.champs:
        if decode64(champ.champDescriptorId) in champs_text_db_labels:
            data[champs_text_db_labels[decode64(champ.champDescriptorId)]] = (
                champ.stringValue
            )
        elif decode64(champ.champDescriptorId) in champs_checkbox_db_labels:
            data[champs_checkbox_db_labels[decode64(champ.champDescriptorId)]] = (
                champ.checked
            )
        elif decode64(champ.champDescriptorId) in champs_date_db_labels:
            data[champs_date_db_labels[decode64(champ.champDescriptorId)]] = champ.date
        elif decode64(champ.champDescriptorId) in champs_integer_number_db_labels:
            data[champs_integer_number_db_labels[decode64(champ.champDescriptorId)]] = (
                int(champ.stringValue)
            )
        elif decode64(champ.champDescriptorId) in champs_repetition_db_labels:
            pass
        elif decode64(champ.champDescriptorId) == "Champ-3988475":
            data["fichier_tableau_suivi_camion_citerne"] = process_piece_justificative(
                champ,
                f"demandes_simplifiees/{now.strftime('%Y-%m-%d')}/{current_dossier.number}/fichier_tableau_suivi_camion_citerne/",
            )
        else:
            pass
            # print(decode64(champ.champDescriptorId))
            # print(champ)
    return PreprocessedDossierSerializer.validate(data)


def process_dossiers(dossiers: List[Dossier]):
    processed_dossiers = []
    for node_id in range(len(dossiers)):
        curr_node = dossiers[node_id]
        processed_dossiers.append(process_dossier(curr_node))
    return processed_dossiers


def get_avis(dossiers: List[Dossier]):
    enriched_avis = []
    now = datetime.datetime.now()
    for dossier in dossiers:
        if dossier.avis:
            for curr_avis in dossier.avis:
                new_enriched_avis_data = {
                    "id_dossier": dossier.number,
                    "id_avis": curr_avis.id,
                    "question": curr_avis.question,
                    "reponse": curr_avis.reponse,
                    "date_reponse": curr_avis.dateReponse,
                    "date_question": curr_avis.dateQuestion,
                    "claimant_email": curr_avis.claimant.email,
                    "expert_email": curr_avis.expert.email,
                    "pieces_jointes": process_piece_justificative(
                        ListFiles(files=curr_avis.attachments),
                        f"demandes_simplifiees/{now.strftime('%Y-%m-%d')}/{dossier.number}/avis/",
                    ),
                }
                enriched_avis.append(
                    EnrichedAvisSerializer.validate(new_enriched_avis_data)
                )
    return enriched_avis


def get_messages(dossiers: List[Dossier]):
    messages = []
    now = datetime.datetime.now()
    for dossier in dossiers:
        if dossier.messages:
            for curr_message in dossier.messages:
                new_message_data = {
                    "id_message": curr_message.id,
                    "id_dossier": dossier.number,
                    "email": curr_message.email,
                    "body": curr_message.body,
                    "date_creation": curr_message.createdAt,
                    "pieces_jointes": process_piece_justificative(
                        ListFiles(files=curr_message.attachments),
                        f"demandes_simplifiees/{now.strftime('%Y-%m-%d')}/{dossier.number}/messages/",
                    ),
                }
                messages.append(EnrichedMessageSerializer.validate(new_message_data))
    return messages


def get_releve_index(dossiers: List[Dossier]):
    releve_index_list = []
    for dossier in dossiers:
        for champ in dossier.champs:
            if decode64(champ.champDescriptorId) != "Champ-3888549":
                continue
            if not champ.rows:
                continue
            for row_id in range(len(champ.rows)):
                row = champ.rows[row_id]

                new_releve_index = {
                    "id_dossier": dossier.number,
                    "ligne": row_id + 1,
                }
                for row_champ in row.champs:
                    if decode64(row_champ.champDescriptorId) == "Champ-3888598":
                        new_releve_index["date_releve_index"] = row_champ.date
                    if decode64(row_champ.champDescriptorId) == "Champ-3888599":
                        new_releve_index["releve_index"] = row_champ.decimalNumber
                releve_index_list.append(
                    ReleveIndexSerializer.validate(new_releve_index)
                )
    return releve_index_list


def get_volumes_pompes(dossiers: List[Dossier]):
    volumes_pompes_list = []
    for dossier in dossiers:
        for champ in dossier.champs:
            if decode64(champ.champDescriptorId) != "Champ-3888490":
                continue
            if not champ.rows:
                continue
            for row_id in range(len(champ.rows)):
                row = champ.rows[row_id]

                new_volumes_pompes = {
                    "id_dossier": dossier.number,
                    "ligne": row_id + 1,
                }
                for row_champ in row.champs:
                    if decode64(row_champ.champDescriptorId) == "Champ-3888497":
                        new_volumes_pompes["point_prelevement_camion_citerne"] = (
                            row_champ.label
                        )
                    elif decode64(row_champ.champDescriptorId) == "Champ-3888520":
                        new_volumes_pompes["annee_prelevement_camion_citerne_2"] = (
                            row_champ.integerNumber
                        )
                    elif decode64(row_champ.champDescriptorId) == "Champ-3888512":
                        new_volumes_pompes["volumes_pompes_camions_citernes"] = (
                            row_champ.decimalNumber
                        )
                    elif decode64(row_champ.champDescriptorId) == "Champ-3888496":
                        new_volumes_pompes["date_prelevement_camion_citerne"] = (
                            row_champ.date
                        )
                volumes_pompes_list.append(
                    VolumesPompesSerializer.validate(new_volumes_pompes)
                )
    return volumes_pompes_list


def get_extrait_registre(dossiers: List[Dossier]):
    extrait_registre_list = []
    now = datetime.datetime.now()
    for dossier in dossiers:
        for champ in dossier.champs:
            if decode64(champ.champDescriptorId) != "Champ-3915100":
                continue
            if not champ.rows:
                continue
            for row_id in range(len(champ.rows)):
                row = champ.rows[row_id]
                new_extrait_registre = {
                    "id_dossier": dossier.number,
                    "ligne": row_id + 1,
                }
                for row_champ in row.champs:
                    if decode64(row_champ.champDescriptorId) == "Champ-3915102":
                        new_extrait_registre["extraits_registres_papiers"] = (
                            process_piece_justificative(
                                row_champ,
                                f"demandes_simplifiees/{now.strftime('%Y-%m-%d')}/{dossier.number}/extraits_registres_papiers/",
                            )
                        )

                extrait_registre_list.append(
                    ExtraitDeRegistreSerializer.validate(new_extrait_registre)
                )
    return extrait_registre_list


def get_donnees_point_de_prelevement(dossiers: List[Dossier]):
    donnees_point_de_prelevement_list = []
    now = datetime.datetime.now()
    for dossier in dossiers:
        for champ in dossier.champs:
            if decode64(champ.champDescriptorId) != "Champ-3642783":
                continue
            if not champ.rows:
                continue
            for row_id in range(len(champ.rows)):
                row = champ.rows[row_id]
                new_donnees_point_de_prelevement = {
                    "id_dossier": dossier.number,
                    "ligne": row_id + 1,
                }
                for row_champ in row.champs:
                    if decode64(row_champ.champDescriptorId) == "Champ-4017191":
                        new_donnees_point_de_prelevement["nom_point_prelevement"] = (
                            row_champ.values
                        )
                    if decode64(row_champ.champDescriptorId) == "Champ-3642817":
                        new_donnees_point_de_prelevement["fichiers_tableurs"] = (
                            process_piece_justificative(
                                row_champ,
                                f"demandes_simplifiees/{now.strftime('%Y-%m-%d')}/{dossier.number}/fichier_tableur/",
                            )
                        )
                    if decode64(row_champ.champDescriptorId) == "Champ-4017531":
                        new_donnees_point_de_prelevement[
                            "fichiers_autres_documents"
                        ] = process_piece_justificative(
                            row_champ,
                            f"demandes_simplifiees/{now.strftime('%Y-%m-%d')}/{dossier.number}/fichier_autre_document/",
                        )
                donnees_point_de_prelevement_list.append(
                    DonneesPointDePrelevementSerializer.validate(
                        new_donnees_point_de_prelevement
                    )
                )
    return donnees_point_de_prelevement_list


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


def process_standard_v1_file(dossier, file):
    file_extension = get_file_extension(file.object_storage_key)
    if file_extension not in file_extension:
        # TODO: send email
        print(
            f"[{dossier.id_dossier}] Invalid file format. Allowed formats: {file_extension}",
            dossier.adresse_email_declarant,
        )
        return

    try:
        downloaded_file = download_file(settings.SCW_S3_BUCKET, file.object_storage_key)
        with BytesIO(downloaded_file) as file_content:
            print(
                f"[{dossier.id_dossier}]: engine {extract_file_engine[file_extension]}"
            )
            sheets = pd.read_excel(
                file_content,
                engine=extract_file_engine[file_extension],
                sheet_name=None,
            )

            if len(sheets) != 1:
                print(
                    f"[{dossier.id_dossier}] The file should contain only one sheet",
                    dossier.adresse_email_declarant,
                )
                return

            sheet = sheets[next(iter(sheets))]
            tableur = np.vstack([sheet.columns.values, sheet.to_numpy()])
            columns = tuple(
                col.replace("\r", "").replace("\n", "") for col in tableur[2]
            )

            if "Nom du titulaire de l'autorisation de prélèvement" not in tableur[0][0]:
                print(
                    f"[{dossier.id_dossier}] Invalid file format.",
                    dossier.adresse_email_declarant,
                )
                return

            if None in tableur[3:, 0]:
                print(
                    f"[{dossier.id_dossier}]: {file.object_storage_key} contains None in date column"
                )
                return

            if len(set(tableur[3:, 0])) != len(tableur[3:, 0]):
                print(
                    f"[{dossier.id_dossier}]: {file.object_storage_key} contains duplicate dates"
                )
                return

            df_data = {
                "date_releve": [],
                "volume": [],
                "point_prelevement": [],
                "id_dossier": dossier.id_dossier,
                "demarche_data_brute_id": dossier.demarche_data_brute_id,
            }

            for col_id in range(1, len(tableur[0])):
                df_data["date_releve"].extend(tableur[3:, 0])
                df_data["volume"].extend(tableur[3:, col_id])
                df_data["point_prelevement"].extend(
                    [columns[col_id]] * len(tableur[3:, 0])
                )
            df = pd.DataFrame(data=df_data)
            return df

    except Exception as e:
        print(
            f"[{dossier.id_dossier}]: Error processing file {file.object_storage_key}: {e}"
        )


def process_standard_v2_file_a_lire(dossier, sheet):
    if sheet[2, 1] == np.nan:
        print(
            f"[{dossier.id_dossier}]: Nom du point de prelevement n'est pas précisé dans la page A_LIRE"
        )
        return

    return {
        "nom_point_prelevement": sheet[2, 1],
        "nom_point_de_prelevement_associe": sheet[3, 1],
        "remarque_fonctionnement_point_de_prelevement": sheet[4, 1],
    }


def process_standard_v2_file(dossier, file):
    file_extension = get_file_extension(file.object_storage_key)
    if file_extension not in file_extension:
        # TODO: send email
        print(
            f"[{dossier.id_dossier}] Invalid file format. Allowed formats: {file_extension}",
            dossier.adresse_email_declarant,
        )
        return
    try:
        downloaded_file = download_file(settings.SCW_S3_BUCKET, file.object_storage_key)
        with BytesIO(downloaded_file) as file_content:
            print(
                f"[{dossier.id_dossier}]: engine {extract_file_engine[file_extension]}"
            )
            sheets = pd.read_excel(
                file_content,
                engine=extract_file_engine[file_extension],
                sheet_name=None,
            )
            sheets = {key.replace(" ", "_"): value for key, value in sheets.items()}

            if tuple(sheets.keys()) != tuple_fichier_standard_v2_onglets:
                print(f"[{dossier.id_dossier}]: les onglets ne sont pas corrects")
                return

            first_sheet = sheets[tuple_fichier_standard_v2_onglets[0]]
            first_sheet = np.vstack(
                [first_sheet.columns.values, first_sheet.to_numpy()]
            )

            common_data = process_standard_v2_file_a_lire(dossier, first_sheet)

            common_data["id_dossier"] = dossier.id_dossier
            common_data["demarche_data_brute_id"] = dossier.demarche_data_brute_id
            list_df = []

            for curr_sheet_id in range(2, len(tuple_fichier_standard_v2_onglets)):
                curr_sheet = sheets[tuple_fichier_standard_v2_onglets[curr_sheet_id]]
                curr_sheet = np.vstack(
                    [curr_sheet.columns.values, curr_sheet.to_numpy()]
                )

                if len(curr_sheet[1:, 1]) <= 11:
                    continue
                for i in range(2, len(curr_sheet[1, :])):
                    if not (
                        pd.isna(curr_sheet[1, i])
                        or curr_sheet[1, i] == ""
                        or curr_sheet[1, i] is None
                        or curr_sheet[1, i] == "nan"
                    ):
                        df = pd.DataFrame(
                            {
                                "date": curr_sheet[12:, 0],
                                "heure": curr_sheet[12:, 1],
                                "valeur": curr_sheet[12:, i],
                                "nom_parametre": curr_sheet[1, i],
                                "type": curr_sheet[2, i],
                                "frequence": curr_sheet[3, i],
                                "unite": curr_sheet[4, i],
                                "detail_point_suivi": curr_sheet[5, i],
                                "profondeur": curr_sheet[6, i],
                                "date_debut": curr_sheet[7, i],
                                "date_fin": curr_sheet[8, i],
                                "remarque": curr_sheet[9, i],
                            }
                            | common_data
                        )
                        list_df.append(df)
            return pd.concat(list_df, ignore_index=True)
    except Exception as e:
        print(
            f"[{dossier.id_dossier}]: Error processing file {file.object_storage_key}: {e}"
        )
