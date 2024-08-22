import pandas as pd
from airflow.models import BaseOperator
from sqlalchemy import select

from utils.common.exceptions import FileError
from utils.db.init_db import get_local_session
from utils.demarchessimplifiees.common.schemas import DossierState
from utils.demarchessimplifiees.data_extractions.models import (
    CiterneReleve,
    DonneesPointDePrelevement,
    PrelevementReleve,
    PreprocessedDossier,
)
from utils.demarchessimplifiees.standard_files_extractions.services import (
    accepte_dossier_if_not_accepted,
    process_aep_or_zre_file,
    process_standard_citerne_file,
    replace_nan_by_none,
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
                PreprocessedDossier.demarche_data_brute_id == demarche_data_brute_id,
                PreprocessedDossier.type_prelevement
                == "Prélèvement par camion citerne",
                PreprocessedDossier.etat_dossier.in_(
                    [DossierState.EN_INSTRUCTION.value, DossierState.ACCEPTE.value]
                ),
            )
            for current_dossier_row in session.execute(query):
                dossier = current_dossier_row[0]
                if not dossier.fichier_tableau_suivi_camion_citerne:
                    continue

                current_dossier_dfs = []
                dossier_errors = []
                for file in dossier.fichier_tableau_suivi_camion_citerne:
                    try:
                        file_df = process_standard_citerne_file(dossier, file)
                        if file_df is not None:
                            current_dossier_dfs.append(file_df)
                    except FileError as e:
                        dossier_errors.append(e.get_message_to_send())

                if dossier_errors:
                    send_error_mail(
                        dossier,
                        "\n".join(dossier_errors),
                        demarche_data_brute_id,
                        session,
                    )
                else:
                    if current_dossier_dfs:
                        dossiers_dfs += current_dossier_dfs
                    accepte_dossier_if_not_accepted(dossier)

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
        query_dossier = select(PreprocessedDossier).where(
            PreprocessedDossier.demarche_data_brute_id == demarche_data_brute_id,
            PreprocessedDossier.type_prelevement == "Prélèvement AEP ou en ZRE",
            PreprocessedDossier.etat_dossier.in_(
                [DossierState.EN_INSTRUCTION.value, DossierState.ACCEPTE.value]
            ),
        )

        with get_local_session() as session:
            donnees_point_de_prelevements = session.execute(query_dossier).all()
            for (dossier,) in donnees_point_de_prelevements:
                query_point_de_prelevement = select(DonneesPointDePrelevement).where(
                    DonneesPointDePrelevement.id_dossier == dossier.id_dossier,
                    DonneesPointDePrelevement.demarche_data_brute_id
                    == demarche_data_brute_id,
                )
                try:
                    dossier_data = []
                    dossier_errors = []
                    for (donnees_point_de_prelevement,) in session.execute(
                        query_point_de_prelevement
                    ).all():
                        for (
                            fichier_tableur
                        ) in donnees_point_de_prelevement.fichiers_tableurs:
                            try:
                                dossier_data += process_aep_or_zre_file(
                                    donnees_point_de_prelevement,
                                    dossier,
                                    fichier_tableur,
                                )
                            except FileError as e:
                                dossier_errors.append(e.get_message_to_send())
                    if dossier_errors:
                        send_error_mail(
                            dossier,
                            "\n".join(dossier_errors),
                            demarche_data_brute_id,
                            session,
                        )
                    else:
                        current_dossier_prelevement = [
                            PrelevementReleve(
                                demarche_data_brute_id=demarche_data_brute_id,
                                id_dossier=dossier.id_dossier,
                                date=row["date"],
                                valeur=replace_nan_by_none(row["valeur"]),
                                nom_parametre=row["nom_parametre"],
                                type=row["type"],
                                frequence=row["frequence"],
                                unite=row["unite"],
                                detail_point_suivi=replace_nan_by_none(
                                    row["detail_point_suivi"]
                                ),
                                remarque_serie_donnees=replace_nan_by_none(
                                    row["remarque_serie_donnees"]
                                ),
                                remarque=replace_nan_by_none(row["remarque"]),
                                profondeur=replace_nan_by_none(row["profondeur"]),
                                date_debut=row["date_debut"],
                                date_fin=row["date_fin"],
                                nom_point_prelevement=row["nom_point_prelevement"],
                                nom_point_de_prelevement_associe=replace_nan_by_none(
                                    row["nom_point_de_prelevement_associe"]
                                ),
                                remarque_fonctionnement_point_de_prelevement=replace_nan_by_none(
                                    row["remarque_fonctionnement_point_de_prelevement"]
                                ),
                            )
                            for row in dossier_data
                        ]
                        session.add_all(current_dossier_prelevement)
                        session.commit()
                        accepte_dossier_if_not_accepted(dossier)
                except Exception as e:
                    raise Exception(
                        f"Error while processing dossier {dossier.id_dossier}) : {e}"
                    )
