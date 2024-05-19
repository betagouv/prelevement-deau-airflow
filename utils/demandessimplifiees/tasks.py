import hashlib
import json
import uuid

from airflow.models import BaseOperator

from utils.db.session import local_session
from utils.demandessimplifiees.models import DemarcheDataBrute
from utils.demandessimplifiees.models import DonneesPointDePrelevement
from utils.demandessimplifiees.models import ExtraitDeRegistre
from utils.demandessimplifiees.models import PreprocessedDossier
from utils.demandessimplifiees.models import ReleveIndex
from utils.demandessimplifiees.models import VolumesPompes
from utils.demandessimplifiees.services import get_demarche
from utils.demandessimplifiees.services import get_demarche_from_demarches_simplifiees
from utils.demandessimplifiees.services import get_donnees_point_de_prelevement
from utils.demandessimplifiees.services import get_extrait_registre
# from utils.demandessimplifiees.services import get_avis
from utils.demandessimplifiees.services import get_releve_index
from utils.demandessimplifiees.services import get_volumes_pompes
from utils.demandessimplifiees.services import process_dossiers
from utils.demandessimplifiees.services import (
    save_demarche_to_file,
)


class CollectDemarcheOperator(BaseOperator):
    def __init__(self, demarche_number: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.demarche_number = demarche_number

    def execute(self, context):
        sha256_hash = hashlib.sha256()
        collected_data = get_demarche_from_demarches_simplifiees(self.demarche_number)
        collected_data_json = json.loads(collected_data)
        if "errors" in collected_data_json:
            raise Exception(f"Error while collecting data: {collected_data_json['errors']}")

        demarche_data_brute_id = uuid.uuid4()

        demarche = get_demarche(collected_data_json)
        processed_dossiers = process_dossiers(demarche.dossiers.nodes)
        # avis = get_avis(demarche.dossiers.nodes)
        releve_index = get_releve_index(demarche.dossiers.nodes)
        volumes_pompes = get_volumes_pompes(demarche.dossiers.nodes)
        extraits_registres = get_extrait_registre(demarche.dossiers.nodes)
        donnees_point_de_prelevement = get_donnees_point_de_prelevement(demarche.dossiers.nodes)
        donnees_point_de_prelevement_db = [
            DonneesPointDePrelevement(**dpp.dict(), demarche_data_brute_id=demarche_data_brute_id) for dpp in
            donnees_point_de_prelevement]
        extraits_registres_db = [ExtraitDeRegistre(**er.dict(), demarche_data_brute_id=demarche_data_brute_id) for er in
                                 extraits_registres]
        volumes_pompes_db = [VolumesPompes(**vp.dict(), demarche_data_brute_id=demarche_data_brute_id) for vp in
                             volumes_pompes]
        releve_index_db = [ReleveIndex(**ri.dict(), demarche_data_brute_id=demarche_data_brute_id) for ri in
                           releve_index]
        processed_dossiers_db = [PreprocessedDossier(**ppd.dict(), demarche_data_brute_id=demarche_data_brute_id) for
                                 ppd in processed_dossiers]

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
                    id=demarche_data_brute_id,
                    hashed_collected_data=hashed_collected_data,
                    file_path=file_path,
                    demarche_number=self.demarche_number
                )
                print("Data is created")
                session.add(new_demarche_data_brute)
                session.commit()
                session.refresh(new_demarche_data_brute)
                new_demarche_data_brute.donnees_point_de_prelevements = donnees_point_de_prelevement_db
                new_demarche_data_brute.extrait_de_registres = extraits_registres_db
                new_demarche_data_brute.volumes_pompes = volumes_pompes_db
                new_demarche_data_brute.releve_index = releve_index_db
                session.add_all(donnees_point_de_prelevement_db)
                session.add_all(extraits_registres_db)
                session.add_all(volumes_pompes_db)
                session.add_all(releve_index_db)
                session.add_all(processed_dossiers_db)
                session.commit()
                print(f"Data collected and saved with id {new_demarche_data_brute.id}")
            except Exception as e:
                print(f"Error while saving data: {e}")
                session.rollback()
                raise e
            finally:
                session.close()
        return hashed_collected_data
