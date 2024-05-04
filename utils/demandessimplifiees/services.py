import os

import requests

from utils.core.settings import settings
from utils.core.tools import open_file, write_file


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
            "variables": {"demarcheNumber": demarche_number, "includeDossiers": True},
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
