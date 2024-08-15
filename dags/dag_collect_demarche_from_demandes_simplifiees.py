import datetime

from airflow import DAG

from utils.core.settings import settings
from utils.demarchessimplifiees.data_extractions.tasks import CollectDemarcheOperator
from utils.demarchessimplifiees.last_snapshot.tasks import StoreLastSnapshotData
from utils.demarchessimplifiees.merged_to_historical_db.tasks import (
    MergeLastSnapshotOperator,
)
from utils.demarchessimplifiees.standard_files_extractions.tasks import (
    CollectCiterneData,
    CollectPrelevementData,
)
from utils.donnees_historiques.tasks import MergeHistoricalDBOperator

with DAG(
    dag_id="dag_collect_demarche_prelevement_deau",
    start_date=datetime.datetime(2024, 4, 24),
    schedule="@daily",
    catchup=False,
):
    collect_demarches_simplifiees = CollectDemarcheOperator(
        task_id="CollectDemarche", demarche_number=settings.DEMARCHE_ID
    )

    connect_citerne_data = CollectCiterneData(task_id="CollectCiterneData")
    connect_prelevement_data = CollectPrelevementData(task_id="CollectPrelevementData")
    store_last_snapshot_data = StoreLastSnapshotData(task_id="StoreLastSnapshotData")
    merged_last_snapshot = MergeLastSnapshotOperator(
        task_id="MergeLastSnapshotOperator"
    )
    merged_historical_db = MergeHistoricalDBOperator(
        task_id="MergeHistoricalDBOperator"
    )

    collect_demarches_simplifiees >> connect_citerne_data
    collect_demarches_simplifiees >> connect_prelevement_data
    connect_citerne_data >> store_last_snapshot_data
    connect_prelevement_data >> store_last_snapshot_data

    store_last_snapshot_data >> merged_last_snapshot
    merged_last_snapshot >> merged_historical_db
