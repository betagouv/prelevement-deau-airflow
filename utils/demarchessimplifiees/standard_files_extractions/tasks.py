from airflow.models import BaseOperator

from utils.common.logging import get_logger
from utils.demarchessimplifiees.standard_files_extractions.services import (
    changement_etat_citerne_valeur_par_valeur,
    changement_etat_prelevement_autre_type,
    collect_citerne_data,
    collect_prelevement_aep_zre,
)

logging = get_logger(__name__)


class CollectCiterneData(BaseOperator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context):
        collect_citerne_data()


class CollectPrelevementAEPZREData(BaseOperator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context):
        collect_prelevement_aep_zre()


class ChangementEtatValeurParValeurEtAutreType(BaseOperator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context):
        # Ouvrir une session pour interagir avec la base de données
        changement_etat_citerne_valeur_par_valeur()
        changement_etat_prelevement_autre_type()
