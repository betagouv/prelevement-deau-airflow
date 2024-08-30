import datetime

from airflow import DAG

from utils.core.settings import settings
from utils.demarchessimplifiees.data_extraction.tasks import CollectDemarcheOperator
from utils.demarchessimplifiees.standard_files_extractions.tasks import (
    ChangementEtatValeurParValeurEtAutreType,
    CollectCiterneData,
    CollectPrelevementAEPZREData,
)

with DAG(
    dag_id="dag_collect_demarche_prelevement_deau",
    start_date=datetime.datetime(2024, 4, 24),
    schedule="@daily",
    catchup=False,
):
    collect_demarches_simplifiees = CollectDemarcheOperator(
        task_id="CollectDemarche", demarche_number=settings.DEMARCHE_ID
    )

    collect_citerne_data = CollectCiterneData(task_id="CollectCiterneData")
    collect_prelevement_aep_zre = CollectPrelevementAEPZREData(
        task_id="CollectPrelevementAEPZREData"
    )
    changement_etat_valeur_par_valeur_et_autre_type = (
        ChangementEtatValeurParValeurEtAutreType(
            task_id="ChangementEtatValeurParValeurEtAutreType"
        )
    )

    collect_demarches_simplifiees >> collect_prelevement_aep_zre
    collect_demarches_simplifiees >> collect_citerne_data
    collect_demarches_simplifiees >> changement_etat_valeur_par_valeur_et_autre_type
