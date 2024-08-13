import logging

import numpy as np
import pandas as pd
from airflow.models import BaseOperator
from sqlalchemy import select

from utils.common.exceptions import FileError
from utils.common.utils import encode64
from utils.core.settings import settings
from utils.db.init_db import get_local_session
from utils.demarchessimplifiees.common.schemas import CorrectionReasonEnum, DossierState
from utils.demarchessimplifiees.data_extractions.models import (
    CiterneReleve,
    PrelevementReleve,
    PreprocessedDossier,
)
from utils.demarchessimplifiees.data_extractions.services import (
    changement_etat_dossier,
    dossier_envoyer_message,
)
from utils.demarchessimplifiees.errors_management.models import ErrorMail
from utils.demarchessimplifiees.standard_files_extractions.services import (
    get_donnees_point_de_prelevement_by_ddb_id,
    get_preprocessed_dossier,
    process_standard_aep_zre_file,
    process_standard_citerne_file,
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

                    if (
                        (
                            DossierState(dossier.etat_dossier)
                            == DossierState.EN_INSTRUCTION
                        )
                        and (not settings.DRY_RUN)
                        and (settings.DEMARCHE_ID != 80149)
                    ):
                        dossier_accepter_result = changement_etat_dossier(
                            dossier_id=encode64(f"Dossier-{dossier.id_dossier}"),
                            instructeur_id=settings.INSTRUCTEUR_ID,
                            operation="dossierAccepter",
                        )
                        if dossier_accepter_result["data"]["dossierAccepter"]["errors"]:
                            dossier_accepter_result_errors = ". ".join(
                                [
                                    f"{error['message']}"
                                    for error in dossier_accepter_result["data"][
                                        "dossierAccepter"
                                    ]["errors"]
                                ]
                            )
                            logging.error(
                                f"[{dossier.id_dossier}] {dossier_accepter_result_errors}"
                            )

                except FileError as e:

                    dossier_envoyer_message(
                        dossier_id=encode64(f"Dossier-{dossier.id_dossier}"),
                        instructeur_id=settings.INSTRUCTEUR_ID,
                        body=e.get_message_to_send(),
                        correction=CorrectionReasonEnum.incorrect,
                    )
                    error_mail = ErrorMail(
                        demarche_data_brute_id=demarche_data_brute_id,
                        email=e.email,
                        id_dossier=e.id_dossier,
                        message=e.get_message_to_send(),
                    )
                    session.add(error_mail)
                    logging.error(e.get_message_to_send())
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
        with get_local_session() as session:
            donnees_point_de_prelevement_entries = (
                get_donnees_point_de_prelevement_by_ddb_id(
                    session, demarche_data_brute_id
                )
            )
            if not donnees_point_de_prelevement_entries:
                logging.info("Aucun point de prélèvement trouvé")

            for result in donnees_point_de_prelevement_entries:
                current_donnees_point_de_prelevement = result[0]
                dossier_tuple = get_preprocessed_dossier(
                    session,
                    demarche_data_brute_id,
                    current_donnees_point_de_prelevement.id_dossier,
                )
                dossier = dossier_tuple[0] if dossier_tuple else None
                id_dossier = dossier.id_dossier
                if current_donnees_point_de_prelevement.fichiers_tableurs:

                    for (
                        current_tableur
                    ) in current_donnees_point_de_prelevement.fichiers_tableurs:
                        try:
                            object_storage_key = current_tableur.object_storage_key
                            new_df = process_standard_aep_zre_file(
                                dossier, current_tableur
                            )
                            if new_df is not None and not new_df.empty:
                                new_df = new_df.replace({pd.NaT: None})
                                new_df = new_df.replace({np.nan: None})
                                new_prelevements = new_df.apply(
                                    lambda x: PrelevementReleve(
                                        date=x["date"],
                                        heure=x["heure"],
                                        valeur=x["valeur"],
                                        nom_parametre=x["nom_parametre"],
                                        type=x["type"],
                                        frequence=x["frequence"],
                                        unite=x["unite"],
                                        detail_point_suivi=x["detail_point_suivi"],
                                        profondeur=x["profondeur"],
                                        date_debut=x["date_debut"],
                                        date_fin=x["date_fin"],
                                        remarque=x["remarque"],
                                        nom_point_prelevement=x[
                                            "nom_point_prelevement"
                                        ],
                                        nom_point_de_prelevement_associe=x[
                                            "nom_point_de_prelevement_associe"
                                        ],
                                        remarque_fonctionnement_point_de_prelevement=x[
                                            "remarque_fonctionnement_point_de_prelevement"
                                        ],
                                        id_dossier=x["id_dossier"],
                                        demarche_data_brute_id=demarche_data_brute_id,
                                    ),
                                    axis=1,
                                )
                                session.add_all(new_prelevements)
                                session.commit()
                        except FileError as e:
                            if e.sheet_name:
                                logging.error(
                                    f"[{id_dossier}]Erreur dans le processus du fichier {object_storage_key} dans la feuille {e.sheet_name}: {e.MESSAGE}"
                                )
                            else:
                                logging.error(
                                    f"[{id_dossier}]Erreur dans le processus du fichier {object_storage_key}: {e.MESSAGE}"
                                )
                        except Exception as e:
                            logging.error(
                                f"[{id_dossier}]Erreur dans le processus du fichier {object_storage_key}: {str(e)}"
                            )
