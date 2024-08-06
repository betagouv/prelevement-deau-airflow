import datetime

from airflow import DAG

from utils.demarchessimplifiees.merged_to_historical_db.tasks import (
    MergeLastSnapshotOperator,
)
from utils.donnees_historiques.tasks import (
    LoadHistoricalDataOperator,
    MergeHistoricalDBOperator,
)

with DAG(
    dag_id="dag_merge_demandes_simplifiees_to_historical_db",
    start_date=datetime.datetime(2024, 4, 24, hour=1),
    schedule="@daily",
    catchup=False,
):
    load_historical_db = LoadHistoricalDataOperator(task_id="LoadHistoricalData")
    merged_last_snapshot = MergeLastSnapshotOperator(
        task_id="MergeLastSnapshotOperator"
    )
    merged_historical_db = MergeHistoricalDBOperator(
        task_id="MergeHistoricalDBOperator"
    )

    load_historical_db >> merged_last_snapshot
    merged_last_snapshot >> merged_historical_db
