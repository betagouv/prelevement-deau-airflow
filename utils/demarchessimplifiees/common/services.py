import json
import os

import requests

from utils.common.utils import open_file
from utils.core.settings import settings
from utils.demarchessimplifiees.common.schemas import CorrectionReasonEnum


def request_demarches_simplifiees(
    file_path: str, body: dict, token: str = settings.DEMARCHES_SIMPLIFIEES_TOKEN
) -> dict:
    query = open_file(
        path=os.path.join(
            os.getenv("AIRFLOW_HOME"),
            file_path,
        )
    )
    body["query"] = query
    response = requests.post(
        url=settings.DEMARCHES_SIMPLIFIEES_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json=body,
    )

    return json.loads(response.content.decode("utf-8"))


def dossier_envoyer_message(
    dossier_id: str,
    instructeur_id: str,
    body: str,
    correction: CorrectionReasonEnum = None,
    token: str = None,
) -> dict:
    return request_demarches_simplifiees(
        file_path="utils/demarchessimplifiees/gql_queries/dossier_envoyer_message.gql",
        body={
            "variables": {
                "input": {
                    "dossierId": dossier_id,
                    "instructeurId": instructeur_id,
                    "body": body,
                    "correction": correction.value if correction else None,
                },
            },
            "operationName": "dossierEnvoyerMessage",
        },
        token=token,
    )


def changement_etat_dossier(dossier_id: str, instructeur_id: str, operation) -> dict:
    return request_demarches_simplifiees(
        file_path="utils/demarchessimplifiees/gql_queries/changement_etat_dossier.gql",
        body={
            "variables": {
                "input": {
                    "dossierId": dossier_id,
                    "instructeurId": instructeur_id,
                },
            },
            "operationName": operation,
        },
    )
