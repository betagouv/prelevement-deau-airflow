import datetime

from airflow import DAG

from utils.demandessimplifiees.tasks import CollectDemarcheOperator

with DAG(
    dag_id="dag_collect_demarche_prelevement_deau",
    start_date=datetime.datetime(2024, 4, 24),
    schedule="@weekly",
):
    CollectDemarcheOperator(task_id="CollectDemarche", demarche_number=80149)
