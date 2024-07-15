import datetime

from airflow import DAG

from utils.demarchessimplifiees.merged_to_historical_db.tasks import (
    MergeLastSnapshotOperator,
)

with DAG(
    dag_id="dag_merge_demandes_simplifiees_to_historical_db",
    start_date=datetime.datetime(2024, 4, 24),
    schedule="@weekly",
    catchup=False,
):
    MergeLastSnapshotOperator(task_id="merge_last_snapshot")
