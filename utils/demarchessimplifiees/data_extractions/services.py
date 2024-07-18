import copy
import datetime
import os
import uuid
from typing import List

import requests

from utils.common.logging import get_logger
from utils.common.object_storage_client import upload_file
from utils.common.utils import decode64
from utils.core.settings import settings
from utils.core.tools import open_file, write_file
from utils.demarchessimplifiees.common.constant import (
    champs_checkbox_db_labels,
    champs_date_db_labels,
    champs_integer_number_db_labels,
    champs_repetition_db_labels,
    champs_text_db_labels,
)
from utils.demarchessimplifiees.common.schemas import (
    Champ,
    ChampType,
    CheckboxChamp,
    DateChamp,
    DecimalNumberChamp,
    Demarche,
    DonneesPointDePrelevementSerializer,
    DossierSerializer,
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

logging = get_logger(__name__)


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


def process_dossier(
    current_dossier: DossierSerializer,
) -> PreprocessedDossierSerializer:
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


def process_dossiers(dossiers: List[DossierSerializer]):
    processed_dossiers = []
    for node_id in range(len(dossiers)):
        curr_node = dossiers[node_id]
        processed_dossiers.append(process_dossier(curr_node))
    return processed_dossiers


def get_avis(dossiers: List[DossierSerializer]):
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


def get_messages(dossiers: List[DossierSerializer]):
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


def get_releve_index(dossiers: List[DossierSerializer]):
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


def get_volumes_pompes(dossiers: List[DossierSerializer]):
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


def get_extrait_registre(dossiers: List[DossierSerializer]):
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


def get_donnees_point_de_prelevement(dossiers: List[DossierSerializer]):
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
