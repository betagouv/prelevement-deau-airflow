import copy
from typing import List

import requests

from utils.common.logging import get_logger
from utils.common.object_storage_client import upload_file
from utils.common.utils import decode64
from utils.core.settings import settings
from utils.db.init_db import get_local_session
from utils.demarchessimplifiees.common.constant import champs_to_labels
from utils.demarchessimplifiees.common.services import request_demarches_simplifiees
from utils.demarchessimplifiees.data_extraction.models import (
    Avis,
    AvisPieceJointe,
    DonneesPointDePrelevementAPEZRE,
    Dossier,
    Message,
    MessagePieceJointe,
    PrelevementCiterneValeurParValeur,
    ReleverIndex,
)
from utils.demarchessimplifiees.data_extraction.schemas import (
    Champ,
    ChampType,
    CheckboxChamp,
    DateChamp,
    DecimalNumberChamp,
    Demarche,
    DossierEtatEnum,
    DossierSerializer,
    DossierSousEtatEnum,
    FileSerializer,
    InputAvisSerializer,
    InputDossierSerializer,
    InputMessageSerializer,
    IntegerNumberChamp,
    MultipleDropDownListChamp,
    PieceJustificativeChamp,
    RepetitionChamp,
    TextChamp,
    TypePrelevementEnum,
    TypeTransmissionDonneesEnum,
)

logging = get_logger(__name__)


def get_demarche_from_demarches_simplifiees_page(
    demarche_number: int, after: str = None
) -> dict:
    return request_demarches_simplifiees(
        file_path="utils/demarchessimplifiees/gql_queries/get_demarche.gql",
        body={
            "variables": {
                "demarcheNumber": demarche_number,
                "includeDossiers": True,
                "includeAvis": True,
                "includeMessages": True,
                "after": after,
            },
            "operationName": "getDemarche",
        },
    )


def get_demarche_from_demarches_simplifiees(demarche_number: int) -> dict:
    demarche_dict = get_demarche_from_demarches_simplifiees_page(demarche_number)
    if "errors" in demarche_dict:
        raise Exception(f"Une erreur est survenue: {demarche_dict['errors']}")

    has_next_page = demarche_dict["data"]["demarche"]["dossiers"]["pageInfo"][
        "hasNextPage"
    ]

    while has_next_page:
        next_cursor = demarche_dict["data"]["demarche"]["dossiers"]["pageInfo"][
            "endCursor"
        ]
        new_response = get_demarche_from_demarches_simplifiees_page(
            demarche_number, next_cursor
        )
        demarche_dict["data"]["demarche"]["dossiers"]["nodes"] += new_response["data"][
            "demarche"
        ]["dossiers"]["nodes"]
        demarche_dict["data"]["demarche"]["dossiers"]["pageInfo"] = new_response[
            "data"
        ]["demarche"]["dossiers"]["pageInfo"]
        has_next_page = new_response["data"]["demarche"]["dossiers"]["pageInfo"][
            "hasNextPage"
        ]

    return demarche_dict


def champ_to_pytandic(champ: dict):
    if "__typename" not in champ:
        raise Exception("PAS UN CHAMP")
    champ["champType"] = champ["__typename"]
    if champ["__typename"] == ChampType.CHECKBOX.value:
        return CheckboxChamp.model_validate(champ)
    elif champ["__typename"] == ChampType.DATE.value:
        return DateChamp.model_validate(champ)
    elif champ["__typename"] == ChampType.INTEGER_NUMBER.value:
        return IntegerNumberChamp.model_validate(champ)
    elif champ["__typename"] == ChampType.TEXT.value:
        return TextChamp.model_validate(champ)
    elif champ["__typename"] == ChampType.PIECE_JUSTIFICATIVE.value:
        return PieceJustificativeChamp.model_validate(champ)
    elif champ["__typename"] == ChampType.DECIMAL_NUMBER.value:
        return DecimalNumberChamp.model_validate(champ)
    elif champ["__typename"] == ChampType.MULTIPLE_DROPDOWN_LIST.value:
        return MultipleDropDownListChamp.model_validate(champ)
    elif champ["__typename"] == ChampType.REPETITION.value:
        if champ["rows"]:
            nb_rows = len(champ["rows"])
            for r_id in range(nb_rows):
                champ["rows"][r_id]["champs"] = champs_to_pydantic(
                    champ["rows"][r_id]["champs"]
                )
        return RepetitionChamp.model_validate(champ)
    else:
        raise Exception(f"le typename non connu: {champ['__typename']}")


def champs_to_pydantic(champs: List[dict]):
    processed_champs: List[Champ] = []
    for champ in champs:
        processed_champs.append(champ_to_pytandic(champ))
    return processed_champs


def get_demarche(demarches_simplfiees_data: dict) -> Demarche:
    current_demarche_dict = copy.deepcopy(demarches_simplfiees_data)
    for node_id in range(
        len(current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"])
    ):
        current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"][node_id][
            "champs"
        ] = champs_to_pydantic(
            current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"][node_id][
                "champs"
            ]
        )

        current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"][node_id][
            "annotations"
        ] = champs_to_pydantic(
            current_demarche_dict["data"]["demarche"]["dossiers"]["nodes"][node_id][
                "annotations"
            ]
        )
    current_demarche = Demarche.model_validate(
        current_demarche_dict["data"]["demarche"]
    )
    return current_demarche


def process_file(
    filename: str,
    url: str,
    object_storage: str,
):
    download_file_response = requests.get(url)
    upload_file(
        settings.SCW_S3_BUCKET,
        object_storage,
        download_file_response.content,
        acl="bucket-owner-read",
    )
    return {"filename": filename, "url": url, "object_storage": object_storage}


def process_prelevement_citerne_file(dossier_id: int, champ: PieceJustificativeChamp):
    object_storage = f"demarches_simplifiees/dossiers/{dossier_id}/fichier_tableau_suivi_camion_citerne/{champ.files[0].filename}"
    return process_file(champ.files[0].filename, champ.files[0].url, object_storage)


def process_message_piece_jointe(
    dossier_id: int, message_id: int, champ: FileSerializer
):
    object_storage = f"demarches_simplifiees/dossiers/{dossier_id}/messages/{message_id}/pieces_jointes/{champ.filename}"
    return process_file(champ.filename, champ.url, object_storage)


def process_avis_piece_jointe(dossier_id: int, avis_id: int, champ: FileSerializer):
    object_storage = f"demarches_simplifiees/dossiers/{dossier_id}/avis/{avis_id}/pieces_jointes/{champ.filename}"
    return process_file(champ.filename, champ.url, object_storage)


def get_prelevement_citerne_valeur_par_valeur(champ: RepetitionChamp):
    result = []

    for row in champ.rows:
        result.append(
            {
                "nom_point_prelevement": row.champs[0].stringValue,
                "date": row.champs[1].date,
                "valeur": row.champs[2].decimalNumber,
            }
        )
    return result


def get_prelevement_citerne_volume_pompe(champ: RepetitionChamp):
    result = []

    for row in champ.rows:
        result.append(
            {
                "nom_point_prelevement": row.champs[0].stringValue,
                "annee": row.champs[1].integerNumber,
                "valeur": row.champs[2].decimalNumber,
            }
        )

    return result


def process_prelevement_zre_or_icpe(dossier_id: int, champ: RepetitionChamp):
    result = []

    for row_id in range(len(champ.rows)):
        row = champ.rows[row_id]

        ficher_prelevement = row.champs[1].files[0]

        fichier_object_storage = f"demarches_simplifiees/dossiers/{dossier_id}/prelevement_aep_zre/{row_id}/fichier_prelevement_{ficher_prelevement.filename}"
        response = requests.get(ficher_prelevement.url)
        upload_file(
            settings.SCW_S3_BUCKET,
            fichier_object_storage,
            response.content,
            acl="bucket-owner-read",
        )

        row_result = {
            "nom_point_prelevement": row.champs[0].stringValue,
            "fichier_prelevement_filename": ficher_prelevement.filename,
            "fichier_prelevement_url": ficher_prelevement.url,
            "fichier_prelevement_object_storage": fichier_object_storage,
            "ligne": row_id + 1,
        }

        if row.champs[2].files:
            autre_document = row.champs[2].files[0]

            autre_document_object_storage = f"demarches_simplifiees/dossiers/{dossier_id}/prelevement_aep_zre/{row_id}/autre_document_{autre_document.filename}"
            response = requests.get(autre_document.url)
            upload_file(
                settings.SCW_S3_BUCKET,
                autre_document_object_storage,
                response.content,
                acl="bucket-owner-read",
            )

            row_result["autre_document_suivi_filename"] = autre_document.filename
            row_result["autre_document_suivi_url"] = autre_document.url
            row_result["autre_document_suivi_object_storage"] = (
                autre_document_object_storage
            )
        result.append(row_result)
    return result


def process_autre_prelevement(
    champ: RepetitionChamp,
):
    result = []
    for row_id in range(len(champ.rows)):
        row = champ.rows[row_id]

        result.append(
            {"date": row.champs[0].date, "valeur": row.champs[1].decimalNumber}
        )
    return result


def get_sous_etat_dossier(
    current_dossier: InputDossierSerializer,
):
    if DossierEtatEnum(current_dossier.state) == DossierEtatEnum.EN_CONSTRUCTION:
        if current_dossier.datePassageEnInstruction:
            if current_dossier.dateDerniereCorrectionEnAttente:
                return DossierSousEtatEnum.EN_ATTENTE_DE_CORRECTION
            else:
                return DossierSousEtatEnum.CORRIGE

    return None


def process_message(dossier_id: int, message: InputMessageSerializer):
    data = {
        "id": int(decode64(message.id).split("-")[1]),
        "body": message.body,
        "email": message.email,
        "date_creation": message.createdAt,
        "pieces_jointes": [],
    }

    for piece_jointe in message.attachments:
        processed_piece_jointe = process_message_piece_jointe(
            dossier_id, data["id"], piece_jointe
        )
        data["pieces_jointes"].append(processed_piece_jointe)
    return data


def process_avis(dossier_id: int, avis: InputAvisSerializer):
    data = {
        "id": int(decode64(avis.id).split("-")[1]),
        "question": avis.question,
        "reponse": avis.reponse,
        "date_question": avis.dateQuestion,
        "date_reponse": avis.dateReponse,
        "email_claimant": avis.claimant.email,
        "email_expert": avis.expert.email,
        "pieces_jointes": [],
    }

    for piece_jointe in avis.attachments:
        processed_piece_jointe = process_message_piece_jointe(
            dossier_id, data["id"], piece_jointe
        )
        data["pieces_jointes"].append(processed_piece_jointe)
    return data


def process_dossier(
    current_dossier: InputDossierSerializer,
) -> DossierSerializer:
    data = {}
    dict_id_to_champs = {}
    for champ in current_dossier.champs:
        decoded_id = decode64(champ.champDescriptorId)
        dict_id_to_champs[champs_to_labels[decoded_id]] = champ

    for annotation in current_dossier.annotations:
        decoded_id = decode64(annotation.champDescriptorId)
        if annotation.champType == ChampType.TEXT and annotation.stringValue:
            dict_id_to_champs[champs_to_labels[decoded_id]] = annotation
        elif annotation.champType == ChampType.PIECE_JUSTIFICATIVE and annotation.files:
            dict_id_to_champs[champs_to_labels[decoded_id]] = annotation

    if (
        "mode_transmission_donnees_camion_citerne" in dict_id_to_champs
        and dict_id_to_champs["mode_transmission_donnees_camion_citerne"].stringValue
        == "En déposant le registre au format tableur (tableau Excel)"
    ):
        dict_id_to_champs["mode_transmission_donnees_camion_citerne"].stringValue = (
            TypeTransmissionDonneesEnum.TABLEAU_SUIVI.value
        )

    # CAMION CITERNE
    if (
        TypePrelevementEnum(dict_id_to_champs["type_prelevement"].stringValue)
        == TypePrelevementEnum.PRELEVEMENT_CAMION_CITERNE
    ):

        # VOLUME POMPE
        if (
            dict_id_to_champs["annee_prelevement_camion_citerne"].stringValue == "2023"
            and "prelevement_points_autorises_aot_2023" in dict_id_to_champs
            and dict_id_to_champs["prelevement_points_autorises_aot_2023"].checked
            and dict_id_to_champs["details_prelevements_camion_citerne"].checked
            is False
        ):
            dict_id_to_champs["prelevement_citerne_valeur_par_valeur"] = (
                get_prelevement_citerne_volume_pompe(
                    dict_id_to_champs["prelevement_citerne_valeur_par_valeur_tmp"]
                )
            )
        else:
            is_preleve_sur_points_autorises_2023 = (
                "prelevement_points_autorises_aot_2023" in dict_id_to_champs
                and dict_id_to_champs["prelevement_points_autorises_aot_2023"].checked
            )
            is_preleve_sur_points_autorises_2024 = (
                "prelevement_sur_periode_camion_citerne" in dict_id_to_champs
                and dict_id_to_champs["prelevement_sur_periode_camion_citerne"].checked
            )

            if (
                is_preleve_sur_points_autorises_2023
                or is_preleve_sur_points_autorises_2024
            ):
                if (
                    TypeTransmissionDonneesEnum(
                        dict_id_to_champs[
                            "mode_transmission_donnees_camion_citerne"
                        ].stringValue
                    )
                    == TypeTransmissionDonneesEnum.TABLEAU_SUIVI
                ):
                    processed_file = process_prelevement_citerne_file(
                        current_dossier.number,
                        dict_id_to_champs["fichier_tableau_suivi_camion_citerne"],
                    )
                    dict_id_to_champs[
                        "fichier_tableau_suivi_camion_citerne_filename"
                    ] = processed_file["filename"]
                    dict_id_to_champs["fichier_tableau_suivi_camion_citerne_url"] = (
                        processed_file["url"]
                    )
                    dict_id_to_champs[
                        "fichier_tableau_suivi_camion_citerne_object_storage"
                    ] = processed_file["object_storage"]
                elif (
                    TypeTransmissionDonneesEnum(
                        dict_id_to_champs[
                            "mode_transmission_donnees_camion_citerne"
                        ].stringValue
                    )
                    == TypeTransmissionDonneesEnum.VALEUR_PAR_VALEUR
                ):
                    dict_id_to_champs["prelevement_citerne_valeur_par_valeur"] = (
                        get_prelevement_citerne_valeur_par_valeur(
                            dict_id_to_champs[
                                "prelevement_citerne_valeur_par_valeur_tmp"
                            ]
                        )
                    )
    # AEP ou ZRE
    elif (
        TypePrelevementEnum(dict_id_to_champs["type_prelevement"].stringValue)
        == TypePrelevementEnum.PRELEVEMENT_APE_ZRE
    ):
        dict_id_to_champs["donnees_point_de_prelevement_aep_zre"] = (
            process_prelevement_zre_or_icpe(
                current_dossier.number,
                dict_id_to_champs["donnees_point_de_prelevement_aep_zre_tmp"],
            )
        )
    # ICPE
    elif (
        TypePrelevementEnum(dict_id_to_champs["type_prelevement"].stringValue)
        == TypePrelevementEnum.PRELEVEMENT_ICPE_HORS_ZRE
    ):
        return None
    # Autre prélèvement
    elif (
        TypePrelevementEnum(dict_id_to_champs["type_prelevement"].stringValue)
        == TypePrelevementEnum.PRELEVEMENT_AUTRE
        and "releve_index_tmp" in dict_id_to_champs
    ):

        dict_id_to_champs["releve_index"] = process_autre_prelevement(
            dict_id_to_champs["releve_index_tmp"]
        )

    # ID
    data["id"] = current_dossier.number
    # Archivé
    data["archive"] = current_dossier.archived
    # État du dossier
    data["etat_dossier"] = current_dossier.state
    # Sous-état du dossier
    data["sous_etat_dossier"] = get_sous_etat_dossier(current_dossier)
    # Dernière mise à jour le
    data["derniere_mise_a_jour"] = current_dossier.dateDerniereModification
    # Déposé le
    data["date_depot"] = current_dossier.dateDepot
    # Passé en instruction le
    data["date_passage_instruction"] = current_dossier.datePassageEnInstruction
    # Date de la dernière correction en attente
    data["date_derniere_correction_en_attente"] = (
        current_dossier.dateDerniereCorrectionEnAttente
    )
    # Traité le
    data["date_traitement"] = current_dossier.dateTraitement
    # Motivation de la décision
    data["motivation_decision"] = current_dossier.motivation
    # Instructeurs
    data["instructeurs"] = ",".join([i.email for i in current_dossier.instructeurs])
    # groupe instructeur
    data["groupe_instructeur"] = current_dossier.groupeInstructeur.label

    # Identité du demandeur
    # Email
    data["adresse_email_connexion"] = current_dossier.usager.email
    # Civilité
    data["civilite_declarant"] = current_dossier.demandeur.civilite
    # Nom
    data["nom_declarant"] = current_dossier.demandeur.nom
    # Prénom
    data["prenom_declarant"] = current_dossier.demandeur.prenom
    # Nom du mandataire
    data["nom_mandataire"] = current_dossier.nomMandataire
    # Prénom du mandataire
    data["prenom_mandataire"] = current_dossier.prenomMandataire
    # Dépôt pour un tiers
    data["depot_pour_mandataire"] = current_dossier.deposeParUnTiers

    # Vos coordonnées
    # Adresse électronique :
    data["adresse_email_declarant"] = dict_id_to_champs[
        "adresse_email_declarant"
    ].stringValue
    # Numéro de téléphone :
    data["numero_telephone_declarant"] = dict_id_to_champs[
        "numero_telephone_declarant"
    ].stringValue
    # Vous formulez cette déclaration en tant que :
    data["statut_declarant"] = dict_id_to_champs["statut_declarant"].stringValue
    # Raison sociale de votre structure :
    data["raison_sociale_structure"] = (
        dict_id_to_champs["raison_sociale_structure"].stringValue
        if "raison_sociale_structure" in dict_id_to_champs
        else None
    )

    # Point de prélèvement d'eau
    # Type de prélèvement :
    data["type_prelevement"] = dict_id_to_champs["type_prelevement"].stringValue
    # Numéro de votre arrêté d'AOT :
    data["numero_arrete_aot"] = (
        dict_id_to_champs["numero_arrete_aot"].stringValue
        if "numero_arrete_aot" in dict_id_to_champs
        else None
    )
    # En quelle année les prélèvements que vous allez déclarer ont-ils été réalisés ? :
    data["annee_prelevement_camion_citerne"] = (
        int(dict_id_to_champs["annee_prelevement_camion_citerne"].stringValue)
        if "annee_prelevement_camion_citerne" in dict_id_to_champs
        else None
    )

    # Prélèvement AEP ou en ZRE
    if (
        TypePrelevementEnum(data["type_prelevement"])
        == TypePrelevementEnum.PRELEVEMENT_APE_ZRE
    ):
        data["donnees_point_de_prelevement_aep_zre"] = dict_id_to_champs[
            "donnees_point_de_prelevement_aep_zre"
        ]  # => 1-N

    # Prélèvement citerne
    if (
        TypePrelevementEnum(data["type_prelevement"])
        == TypePrelevementEnum.PRELEVEMENT_CAMION_CITERNE
    ):
        data["annee_prelevement_camion_citerne"] = dict_id_to_champs[
            "annee_prelevement_camion_citerne"
        ].stringValue
        data["mois_prelevement_camion_citerne"] = (
            dict_id_to_champs["mois_prelevement_camion_citerne"].stringValue
            if "mois_prelevement_camion_citerne" in dict_id_to_champs
            else None
        )

        data["prelevement_sur_periode_camion_citerne"] = (
            dict_id_to_champs["prelevement_sur_periode_camion_citerne"].checked
            if "prelevement_sur_periode_camion_citerne" in dict_id_to_champs
            else None
        )

        data["prelevement_points_autorises_aot_2023"] = (
            dict_id_to_champs["prelevement_points_autorises_aot_2023"].checked
            if "prelevement_points_autorises_aot_2023" in dict_id_to_champs
            else None
        )
        data["mode_transmission_donnees_camion_citerne"] = (
            dict_id_to_champs["mode_transmission_donnees_camion_citerne"].stringValue
            if "mode_transmission_donnees_camion_citerne" in dict_id_to_champs
            else None
        )

        data["fichier_tableau_suivi_camion_citerne_filename"] = (
            dict_id_to_champs["fichier_tableau_suivi_camion_citerne_filename"]
            if "fichier_tableau_suivi_camion_citerne_filename" in dict_id_to_champs
            else None
        )
        data["fichier_tableau_suivi_camion_citerne_url"] = (
            dict_id_to_champs["fichier_tableau_suivi_camion_citerne_url"]
            if "fichier_tableau_suivi_camion_citerne_url" in dict_id_to_champs
            else None
        )
        data["fichier_tableau_suivi_camion_citerne_object_storage"] = (
            dict_id_to_champs["fichier_tableau_suivi_camion_citerne_object_storage"]
            if "fichier_tableau_suivi_camion_citerne_object_storage"
            in dict_id_to_champs
            else None
        )

        data["details_prelevements_camion_citerne"] = (
            dict_id_to_champs["details_prelevements_camion_citerne"].checked
            if "details_prelevements_camion_citerne" in dict_id_to_champs
            else None
        )

        # => 1-N
        data["prelevement_citerne_valeur_par_valeur"] = (
            dict_id_to_champs["prelevement_citerne_valeur_par_valeur"]
            if "prelevement_citerne_valeur_par_valeur" in dict_id_to_champs
            else []
        )

    # Autre prélèvement (agricole, domestique...)
    if (
        TypePrelevementEnum(data["type_prelevement"])
        == TypePrelevementEnum.PRELEVEMENT_AUTRE
    ):
        # Nom du point de prélèvement concerné par la déclaration :
        data["nom_point_prelevement"] = dict_id_to_champs[
            "nom_point_prelevement"
        ].stringValue
        data["date_activation_point_prelevement"] = dict_id_to_champs[
            "date_activation_point_prelevement"
        ].stringValue
        data["prelevement_sur_periode_aot_agricole"] = (
            dict_id_to_champs["prelevement_sur_periode_aot_agricole"].checked
            if "prelevement_sur_periode_aot_agricole" in dict_id_to_champs
            else None
        )
        # Autre prélèvement => 1-N
        data["releve_index"] = (
            dict_id_to_champs["releve_index"]
            if "releve_index" in dict_id_to_champs
            else []
        )

        # Informations sur le compteur
        data["donnees_compteur_volumetrique"] = (
            dict_id_to_champs["donnees_compteur_volumetrique"].checked
            if "donnees_compteur_volumetrique" in dict_id_to_champs
            else None
        )
        data["panne_compteur"] = (
            dict_id_to_champs["panne_compteur"].checked
            if "panne_compteur" in dict_id_to_champs
            else None
        )
        data["index_avant_la_panne_ou_changement_de_compteur"] = (
            dict_id_to_champs[
                "index_avant_la_panne_ou_changement_de_compteur"
            ].decimalNumber
            if "index_avant_la_panne_ou_changement_de_compteur" in dict_id_to_champs
            else None
        )
        data["index_apres_la_panne_ou_changement_de_compteur"] = (
            dict_id_to_champs[
                "index_apres_la_panne_ou_changement_de_compteur"
            ].decimalNumber
            if "index_apres_la_panne_ou_changement_de_compteur" in dict_id_to_champs
            else None
        )
        data["numero_serie_compteur"] = (
            dict_id_to_champs["numero_serie_compteur"].stringValue
            if "numero_serie_compteur" in dict_id_to_champs
            else None
        )
        data["compteur_lecture_directe"] = (
            dict_id_to_champs["compteur_lecture_directe"].stringValue
            if "compteur_lecture_directe" in dict_id_to_champs
            else None
        )
        data["coefficient_multiplicateur_compteur"] = (
            dict_id_to_champs["coefficient_multiplicateur_compteur"].stringValue
            if "coefficient_multiplicateur_compteur" in dict_id_to_champs
            else None
        )

    # Pour finir
    data["commentaire"] = dict_id_to_champs["commentaire"].stringValue
    data["note_facilite_utilisation"] = (
        dict_id_to_champs["note_facilite_utilisation"].stringValue
        if "note_facilite_utilisation" in dict_id_to_champs
        else None
    )
    data["remarque_note"] = (
        dict_id_to_champs["remarque_note"].stringValue
        if "remarque_note" in dict_id_to_champs
        else None
    )
    data["temps_remplissage_questionnaire"] = (
        dict_id_to_champs["temps_remplissage_questionnaire"].stringValue
        if "temps_remplissage_questionnaire" in dict_id_to_champs
        else None
    )
    data["amelioration_temps_remplissage"] = (
        dict_id_to_champs["amelioration_temps_remplissage"].stringValue
        if "amelioration_temps_remplissage" in dict_id_to_champs
        else None
    )
    data["temps_formatage_donnees"] = (
        dict_id_to_champs["temps_formatage_donnees"].stringValue
        if "temps_formatage_donnees" in dict_id_to_champs
        else None
    )
    data["declarant_demarche_simplifiee"] = (
        dict_id_to_champs["declarant_demarche_simplifiee"].stringValue
        if "declarant_demarche_simplifiee" in dict_id_to_champs
        else None
    )
    data["televerseur_tableur_brutes"] = (
        dict_id_to_champs["televerseur_tableur_brutes"].stringValue
        if "televerseur_tableur_brutes" in dict_id_to_champs
        else None
    )
    data["raison_non_declaration_preleveur"] = (
        dict_id_to_champs["raison_non_declaration_preleveur"].stringValue
        if "raison_non_declaration_preleveur" in dict_id_to_champs
        else None
    )
    data["rappel_obligation_mensuelle_declaration"] = (
        dict_id_to_champs["rappel_obligation_mensuelle_declaration"].stringValue
        if "rappel_obligation_mensuelle_declaration" in dict_id_to_champs
        else None
    )
    data["demande_documentation"] = (
        dict_id_to_champs["demande_documentation"].stringValue
        if "demande_documentation" in dict_id_to_champs
        else None
    )
    data["amelioration_documentation"] = (
        ",".join(dict_id_to_champs["amelioration_documentation"].values)
        if "amelioration_documentation" in dict_id_to_champs
        else None
    )
    data["suggestion_informations_visualisation"] = (
        dict_id_to_champs["suggestion_informations_visualisation"].stringValue
        if "suggestion_informations_visualisation" in dict_id_to_champs
        else None
    )
    data["acceptation_contact_deal"] = (
        dict_id_to_champs["acceptation_contact_deal"].checked
        if "acceptation_contact_deal" in dict_id_to_champs
        else None
    )
    data["validation_informations"] = (
        dict_id_to_champs["validation_informations"].checked
        if "validation_informations" in dict_id_to_champs
        else None
    )
    data["date_fin_periode_declaree"] = (
        dict_id_to_champs["date_fin_periode_declaree"].checked
        if "date_fin_periode_declaree" in dict_id_to_champs
        else None
    )
    data["date_debut_periode_declaree"] = (
        dict_id_to_champs["date_debut_periode_declaree"].checked
        if "date_debut_periode_declaree" in dict_id_to_champs
        else None
    )
    # Messages
    data["messages"] = [
        process_message(current_dossier.number, message)
        for message in current_dossier.messages
        if message.body
    ]

    # Avis
    data["avis"] = [
        process_avis(current_dossier.number, avis)
        for avis in current_dossier.avis
        if avis.question
    ]
    return DossierSerializer.model_validate(data)


def get_dossiers(dossiers: List[InputDossierSerializer]) -> List[DossierSerializer]:
    processed_dossiers = []
    for node_id in range(len(dossiers)):
        try:
            curr_node = dossiers[node_id]
            new_dossier = process_dossier(curr_node)
            if new_dossier:
                processed_dossiers.append(new_dossier)
        except Exception as e:
            logging.error(f"Error processing dossier {dossiers[node_id].number}: {e}")
    return processed_dossiers


def collect_demarche(demarche_id: int):
    logging.info(f"Collecte de la démarche {demarche_id} en cours...")
    demarche_data_dict = get_demarche_from_demarches_simplifiees(demarche_id)
    logging.info("Démarche collectée avec succès.")
    demarche = get_demarche(demarche_data_dict)
    logging.info("Démarche traitée avec succès.")
    processed_dossiers = get_dossiers(demarche.dossiers.nodes)
    logging.info("Dossiers traités avec succès.")
    # Ouvrir une session pour interagir avec la base de données
    with get_local_session() as session:
        for dossier in processed_dossiers:
            # Filtrer les dossiers selon leur état
            if DossierEtatEnum(dossier.etat_dossier) in [
                DossierEtatEnum.EN_INSTRUCTION,
                DossierEtatEnum.ACCEPTE,
                DossierEtatEnum.EN_CONSTRUCTION,
            ]:
                current_dossier_dict = dossier.model_dump()

                # Vérifier si le dossier existe déjà
                existing_dossier = (
                    session.query(Dossier)
                    .filter_by(id=current_dossier_dict["id"])
                    .first()
                )

                if existing_dossier:
                    logging.info(
                        f"Le dossier {current_dossier_dict['id']} existe déjà. Suppression en cours..."
                    )
                    # Supprimer le dossier existant et tous les enregistrements associés
                    session.delete(existing_dossier)
                    session.flush()  # S'assurer que la suppression est effectuée

                # Créer les nouveaux prélèvements
                prelevement_citerne_valeur_par_valeurs = [
                    PrelevementCiterneValeurParValeur(**p)
                    for p in current_dossier_dict[
                        "prelevement_citerne_valeur_par_valeur"
                    ]
                ]

                donnees_point_de_prelevement_aep_zre = [
                    DonneesPointDePrelevementAPEZRE(**p)
                    for p in current_dossier_dict[
                        "donnees_point_de_prelevement_aep_zre"
                    ]
                ]

                relever_index = [
                    ReleverIndex(**p) for p in current_dossier_dict["releve_index"]
                ]

                messages = [
                    Message(
                        date_creation=m["date_creation"],
                        email=m["email"],
                        body=m["body"],
                        pieces_jointes=[
                            MessagePieceJointe(
                                filename=pj["filename"],
                                url=pj["url"],
                                object_storage=pj["object_storage"],
                            )
                            for pj in m["pieces_jointes"]
                        ],
                    )
                    for m in current_dossier_dict["messages"]
                ]

                avis = [
                    Avis(
                        question=a["question"],
                        reponse=a["reponse"],
                        date_question=a["date_question"],
                        date_reponse=a["date_reponse"],
                        email_claimant=a["email_claimant"],
                        email_expert=a["email_expert"],
                        pieces_jointes=[
                            AvisPieceJointe(
                                filename=pj["filename"],
                                url=pj["url"],
                                object_storage=pj["object_storage"],
                            )
                            for pj in a["pieces_jointes"]
                        ],
                    )
                    for a in current_dossier_dict["avis"]
                ]

                # Supprimer les champs non pertinents avant de sauvegarder le dossier
                del current_dossier_dict["prelevement_citerne_valeur_par_valeur"]
                del current_dossier_dict["donnees_point_de_prelevement_aep_zre"]
                del current_dossier_dict["releve_index"]
                del current_dossier_dict["messages"]
                del current_dossier_dict["avis"]

                # Sauvegarder le nouveau dossier
                dossier_instance = Dossier(**current_dossier_dict)
                session.add(dossier_instance)
                session.flush()  # S'assurer que le dossier est bien inséré avant d'ajouter les prélèvements
                logging.info(f"Dossier {dossier_instance.id} sauvegardé avec succès.")

                # Ajouter les nouveaux prélèvements
                for prelevement in prelevement_citerne_valeur_par_valeurs:
                    prelevement.id_dossier = dossier_instance.id
                    session.add(prelevement)
                logging.info(
                    f"Prélèvements du dossier {dossier_instance.id} sauvegardés avec succès."
                )

                # Ajouter les données de point de prélèvement AEP ZRE
                for (
                    donnees_point_de_prelevement
                ) in donnees_point_de_prelevement_aep_zre:
                    donnees_point_de_prelevement.id_dossier = dossier_instance.id
                    session.add(donnees_point_de_prelevement)
                logging.info(
                    f"Données de point de prélèvement AEP ZRE du dossier {dossier_instance.id} sauvegardées avec succès."
                )

                # Ajouter les relevés d'index / Autre type de prélèvements
                for index in relever_index:
                    index.id_dossier = dossier_instance.id
                    session.add(index)
                logging.info(
                    f"Relevés d'index / Autre type de prélèvements du dossier {dossier_instance.id} sauvegardés avec succès."
                )

                # Ajouter les messages
                for message in messages:
                    message.id_dossier = dossier_instance.id
                    session.add(message)
                logging.info(
                    f"Messages du dossier {dossier_instance.id} sauvegardés avec succès."
                )

                # Ajouter les avis
                for avi in avis:
                    avi.id_dossier = dossier_instance.id
                    session.add(avi)
                logging.info(
                    f"Avis du dossier {dossier_instance.id} sauvegardés avec succès."
                )

        # Commit des changements
        session.commit()

    logging.info("Dossiers et prélèvements sauvegardés avec succès.")
