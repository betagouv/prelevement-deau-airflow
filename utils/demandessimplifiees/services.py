import base64
import copy
import os
from typing import List

import requests

from utils.core.settings import settings
from utils.core.tools import open_file, write_file
from utils.demandessimplifiees.constant import champs_text_db_labels, champs_checkbox_db_labels, champs_date_db_labels, \
    champs_integer_number_db_labels, champs_repetition_db_labels, champs_piece_justificative_db_labels
from utils.demandessimplifiees.schemas import ChampType, CheckboxChamp, DateChamp, IntegerNumberChamp, TextChamp, \
    PieceJustificativeChamp, DecimalNumberChamp, MultipleDropDownListChamp, RepetitionChamp, Champ, Dossier, \
    PreprocessedDossierSerializer, EnrichedAvis, ReleveIndexSerializer, VolumesPompesSerializer, Demarche, ExtraitDeRegistreSerializer, \
    DonneesPointDePrelevementSerializer


def decode64(code: str):
    encoded_string = code
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string


def get_demarche_from_demarches_simplifiees(demarche_number: int) -> str:
    query = open_file(
        path=os.path.join(
            os.getenv("AIRFLOW_HOME"),
            "utils/demandessimplifiees/gql_queries/get_queries.gql",
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
                "includeMessages": True
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
                champ["rows"][r_id]["champs"] = champs_to_pydantic(champ["rows"][r_id]["champs"])
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
    for n_id in range(len(current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"])):
        current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"][n_id]["champs"] = champs_to_pydantic(
            current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"][n_id]["champs"])
    current_demarche = Demarche.validate(current_demarche_dict["data"]["demarche"])
    return current_demarche


def process_dossier(current_dossier: Dossier):
    data = {}
    # ID
    data["number"] = current_dossier.number
    # Email
    data["email"] = current_dossier.usager.email
    # Civilité
    data["civilite"] = current_dossier.demandeur.civilite
    # Nom
    data["nom"] = current_dossier.demandeur.nom
    # Prénom
    data["prenom"] = current_dossier.demandeur.prenom
    # Dépôt pour un tiers
    data["deposeParUnTiers"] = current_dossier.deposeParUnTiers
    # Nom du mandataire
    data["nomMandataire"] = current_dossier.nomMandataire
    # Prénom du mandataire
    data["prenomMandataire"] = current_dossier.prenomMandataire
    # Archivé
    data["archived"] = current_dossier.archived
    # État du dossier
    data["state"] = current_dossier.state
    # Dernière mise à jour le
    data["dateDerniereModification"] = current_dossier.dateDerniereModification
    # Déposé le
    data["dateDepot"] = current_dossier.dateDepot
    # Passé en instruction le
    data["datePassageEnInstruction"] = current_dossier.datePassageEnInstruction
    # Traité le
    data["dateTraitement"] = current_dossier.dateTraitement
    # Motivation de la décision
    data["motivation"] = current_dossier.motivation
    # Instructeurs
    data["instructeurs"] = current_dossier.instructeurs
    # groupe instructeur
    data["groupe_instructeur"] = current_dossier.groupeInstructeur.label

    for champ in current_dossier.champs:
        if decode64(champ.champDescriptorId) in champs_text_db_labels:
            data[champs_text_db_labels[decode64(champ.champDescriptorId)]] = champ.stringValue
        elif decode64(champ.champDescriptorId) in champs_checkbox_db_labels:
            data[champs_checkbox_db_labels[decode64(champ.champDescriptorId)]] = champ.checked
        elif decode64(champ.champDescriptorId) in champs_date_db_labels:
            data[champs_date_db_labels[decode64(champ.champDescriptorId)]] = champ.date
        elif decode64(champ.champDescriptorId) in champs_integer_number_db_labels:
            data[champs_integer_number_db_labels[decode64(champ.champDescriptorId)]] = int(champ.stringValue)
        elif decode64(champ.champDescriptorId) in champs_repetition_db_labels:
            pass
        elif decode64(champ.champDescriptorId) in champs_piece_justificative_db_labels:
            pass
        else:
            print(champ)
    return PreprocessedDossierSerializer.validate(data)


def process_dossiers(dossiers: List[Dossier]):
    processed_dossiers = []
    for node_id in range(len(dossiers)):
        curr_node = dossiers[node_id]
        processed_dossiers.append(process_dossier(curr_node))
    return processed_dossiers


def get_avis(dossiers: List[Dossier]):
    enriched_avis = []
    for dossier in dossiers:
        if dossier.avis:
            for curr_avis in dossier.avis:
                new_enriched_avis_data = curr_avis.dict()
                new_enriched_avis_data["dossier_id"] = dossier.number
                enriched_avis.append(EnrichedAvis.validate(new_enriched_avis_data))
    return enriched_avis


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
                    "dossier_id": dossier.number,
                    "ligne": row_id + 1,
                }
                for row_champ in row.champs:
                    if decode64(row_champ.champDescriptorId) == "Champ-3888598":
                        new_releve_index["date"] = row_champ.date
                    if decode64(row_champ.champDescriptorId) == "Champ-3888599":
                        new_releve_index["index"] = row_champ.decimalNumber
                releve_index_list.append(ReleveIndexSerializer.validate(new_releve_index))
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
                    "dossier_id": dossier.number,
                    "ligne": row_id + 1,
                }
                for row_champ in row.champs:
                    if decode64(row_champ.champDescriptorId) == "Champ-3888497":
                        new_volumes_pompes["point_prelevement"] = row_champ.label
                    elif decode64(row_champ.champDescriptorId) == "Champ-3888520":
                        new_volumes_pompes["annee"] = row_champ.integerNumber
                    elif decode64(row_champ.champDescriptorId) == "Champ-3888512":
                        new_volumes_pompes["volume_pompe"] = row_champ.decimalNumber
                    elif decode64(row_champ.champDescriptorId) == "Champ-3888496":
                        new_volumes_pompes["date"] = row_champ.date
                volumes_pompes_list.append(VolumesPompesSerializer.validate(new_volumes_pompes))
    return volumes_pompes_list


def get_extrait_registre(dossiers: List[Dossier]):
    extrait_registre_list = []
    for dossier in dossiers:
        for champ in dossier.champs:
            if decode64(champ.champDescriptorId) != "Champ-3915100":
                continue
            if not champ.rows:
                continue
            for row_id in range(len(champ.rows)):
                row = champ.rows[row_id]
                new_extrait_registre = {
                    "dossier_id": dossier.number,
                    "ligne": row_id + 1,
                }
                for row_champ in row.champs:
                    if decode64(row_champ.champDescriptorId) == "Champ-3915102":
                        new_extrait_registre["extrait_registre"] = row_champ

                extrait_registre_list.append(ExtraitDeRegistreSerializer.validate(new_extrait_registre))
    return extrait_registre_list


def get_donnees_point_de_prelevement(dossiers: List[Dossier]):
    donnees_point_de_prelevement_list = []
    for dossier in dossiers:
        for champ in dossier.champs:
            if decode64(champ.champDescriptorId) != "Champ-3642783":
                continue
            if not champ.rows:
                continue
            for row_id in range(len(champ.rows)):
                row = champ.rows[row_id]
                new_donnees_point_de_prelevement = {
                    "dossier_id": dossier.number,
                    "ligne": row_id + 1,
                }
                for row_champ in row.champs:
                    if decode64(row_champ.champDescriptorId) == "Champ-4017191":
                        new_donnees_point_de_prelevement["point_prelevement"] = row_champ.values
                    if decode64(row_champ.champDescriptorId) == "Champ-3642817":
                        new_donnees_point_de_prelevement["donnees_standardisees"] = row_champ
                    if decode64(row_champ.champDescriptorId) == "Champ-4017531":
                        new_donnees_point_de_prelevement["autres_documents"] = row_champ
                donnees_point_de_prelevement_list.append(
                    DonneesPointDePrelevementSerializer.validate(new_donnees_point_de_prelevement))
    return donnees_point_de_prelevement_list
