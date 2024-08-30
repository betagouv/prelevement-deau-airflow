from airflow.models import BaseOperator

from utils.demarchessimplifiees.data_extraction.services import collect_demarche


class CollectDemarcheOperator(BaseOperator):
    def __init__(self, demarche_number: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.demarche_number = demarche_number

    def execute(self, context):
        collect_demarche(self.demarche_number)
