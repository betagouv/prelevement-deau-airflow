import pandas as pd
from airflow.models import BaseOperator
from sqlalchemy import select

from utils.common.exceptions import FileError
from utils.db.init_db import get_local_session
from utils.demarchessimplifiees.common.schemas import DossierState
from utils.demarchessimplifiees.data_extractions.models import (
    CiterneReleve,
    DonneesPointDePrelevement,
    PreprocessedDossier,
)
from utils.demarchessimplifiees.standard_files_extractions.services import (
    accepte_dossier_if_not_accepted,
    process_standard_aep_or_zre_file,
    process_standard_citerne_file,
    send_error_mail,
)


class CollectCiterneData(BaseOperator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context):
        demarche_data_brute_id = context["ti"].xcom_pull(key="demarche_data_brute_id")
        with get_local_session() as session:
            dossiers_dfs = []
            query = select(PreprocessedDossier).where(
                PreprocessedDossier.demarche_data_brute_id == demarche_data_brute_id
            )
            for result in session.execute(query):
                dossier = result[0]
                try:
                    if DossierState(dossier.etat_dossier) not in [
                        DossierState.EN_INSTRUCTION,
                        DossierState.ACCEPTE,
                    ]:
                        continue
                    if dossier.type_prelevement != "Prélèvement par camion citerne":
                        continue
                    if not dossier.fichier_tableau_suivi_camion_citerne:
                        continue

                    current_dossier_dfs = []
                    for file in dossier.fichier_tableau_suivi_camion_citerne:
                        result = process_standard_citerne_file(dossier, file)
                        if result is not None:
                            current_dossier_dfs.append(result)

                    if current_dossier_dfs:
                        dossiers_dfs += current_dossier_dfs

                    accepte_dossier_if_not_accepted(dossier)

                except FileError as e:
                    send_error_mail(dossier, e, demarche_data_brute_id, session)
            df = pd.concat(dossiers_dfs, ignore_index=True)
            df = df[df.date_releve.notna()]
            if not df.empty:
                citernes_releves = df.apply(
                    lambda x: CiterneReleve(
                        date_releve=x["date_releve"],
                        point_prelevement=x["point_prelevement"],
                        volume=x["volume"],
                        demarche_data_brute_id=x["demarche_data_brute_id"],
                        id_dossier=x["id_dossier"],
                    ),
                    axis=1,
                )
                session.add_all(citernes_releves)
                session.commit()


class CollectPrelevementData(BaseOperator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context):
        demarche_data_brute_id = context["ti"].xcom_pull(key="demarche_data_brute_id")

        query = (
            select(DonneesPointDePrelevement, PreprocessedDossier)
            .join(
                PreprocessedDossier,
                DonneesPointDePrelevement.id_dossier == PreprocessedDossier.id_dossier,
            )
            .where(
                DonneesPointDePrelevement.demarche_data_brute_id
                == demarche_data_brute_id,
                PreprocessedDossier.demarche_data_brute_id == demarche_data_brute_id,
                PreprocessedDossier.type_prelevement == "Prélèvement AEP ou en ZRE",
                PreprocessedDossier.etat_dossier.in_(
                    [DossierState.EN_INSTRUCTION.value, DossierState.ACCEPTE.value]
                ),
            )
        )
        with get_local_session() as session:
            donnees_point_de_prelevements = session.execute(query).all()
            for donnees_point_de_prelevment, dossier in donnees_point_de_prelevements:
                try:
                    new_prelevements = process_standard_aep_or_zre_file(
                        donnees_point_de_prelevment, dossier, demarche_data_brute_id
                    )

                    session.add_all(new_prelevements)
                    session.commit()
                    accepte_dossier_if_not_accepted(dossier)
                except FileError as e:
                    send_error_mail(dossier, e, demarche_data_brute_id, session)
                # except Exception as e:
                #    logging.error(f"Error while processing dossier {dossier.id_dossier}: {e}")
