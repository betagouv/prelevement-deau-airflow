import json
import os

import requests

from utils.core.settings import settings
from utils.core.tools import open_file
from utils.demarchessimplifiees.common.schemas import CorrectionReasonEnum


def request_demarches_simplifiees(file_path: str, body: dict):
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
            "Authorization": f"Bearer {settings.DEMARCHES_SIMPLIFIEES_TOKEN}",
        },
        json=body,
    )

    return json.loads(response.content.decode("utf-8"))


def dossier_envoyer_message(
    dossier_id: str,
    instructeur_id: str,
    body: str,
    correction: CorrectionReasonEnum = None,
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
