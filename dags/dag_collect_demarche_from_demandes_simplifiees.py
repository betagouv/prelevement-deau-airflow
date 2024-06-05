import datetime

from airflow import DAG

from utils.demarchessimplifiees.tasks import (
    CollectCiterneData,
    CollectDemarcheOperator,
    CollectPrelevementData,
)

with DAG(
    dag_id="dag_collect_demarche_prelevement_deau",
    start_date=datetime.datetime(2024, 4, 24),
    schedule="@weekly",
):
    collect_demarches_simplifiees = CollectDemarcheOperator(
        task_id="CollectDemarche", demarche_number=80149
    )
    connect_citerne_data = CollectCiterneData(task_id="CollectCiterneData")
    connect_prelevement_data = CollectPrelevementData(task_id="CollectPrelevementData")
    collect_demarches_simplifiees >> connect_citerne_data
    collect_demarches_simplifiees >> connect_prelevement_data
