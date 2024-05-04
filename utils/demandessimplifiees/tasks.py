import hashlib

from airflow.models import BaseOperator

from utils.core.settings import settings
from utils.db.session import local_session
from utils.demandessimplifiees.models import DemarcheDataBrute
from utils.demandessimplifiees.services import (
    get_demarche_from_demarches_simplifiees,
    save_demarche_to_file,
)


class CollectDemarcheOperator(BaseOperator):
    def __init__(self, demarche_number: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.demarche_number = demarche_number

    def execute(self, context):
        sha256_hash = hashlib.sha256()
        collected_data = get_demarche_from_demarches_simplifiees(self.demarche_number)
        sha256_hash.update(collected_data.encode())
        hashed_collected_data = sha256_hash.hexdigest()
        with local_session() as session:
            try:
                if (
                    session.query(DemarcheDataBrute)
                    .filter(
                        DemarcheDataBrute.hashed_collected_data == hashed_collected_data
                    )
                    .first()
                ):
                    print("Data already collected")
                    return
                file_path = save_demarche_to_file(
                    self.demarche_number, collected_data, hashed_collected_data
                )
                new_demarche_data_brute = DemarcheDataBrute(
                    hashed_collected_data=hashed_collected_data,
                    file_path=file_path,
                    demarche_number=self.demarche_number,
                )
                print("Data is created")
                session.add(new_demarche_data_brute)
                session.commit()
                session.refresh(new_demarche_data_brute)
                print(f"Data collected and saved with id {new_demarche_data_brute.id}")
            except Exception as e:
                print(f"Error while saving data: {e}")
                session.rollback()
                raise e
            finally:
                session.close()
        return hashed_collected_data
