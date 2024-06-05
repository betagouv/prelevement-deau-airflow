import hashlib
import json
import uuid

import numpy as np
import pandas as pd
from airflow.models import BaseOperator
from sqlalchemy import select

from utils.common.object_storage_client import upload_file
from utils.core.settings import settings
from utils.db.session import local_session
from utils.demarchessimplifiees.models import (
    Avis,
    CiterneReleve,
    DemarcheDataBrute,
    DonneesPointDePrelevement,
    ExtraitDeRegistre,
    Message,
    PieceJointe,
    PrelevementReleve,
    PreprocessedDossier,
    ReleveIndex,
    VolumesPompes,
)
from utils.demarchessimplifiees.services import (
    get_avis,
    get_demarche,
    get_demarche_from_demarches_simplifiees,
    get_donnees_point_de_prelevement,
    get_donnees_point_de_prelevement_by_ddb_id,
    get_extrait_registre,
    get_messages,
    get_preprocessed_dossier,
    get_releve_index,
    get_volumes_pompes,
    process_dossiers,
    process_standard_v1_file,
    process_standard_v2_file,
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
            raise Exception(
                f"Error while collecting data: {collected_data_json['errors']}"
            )

        demarche_data_brute_id = uuid.uuid4()

        demarche = get_demarche(collected_data_json)
        processed_dossiers = process_dossiers(demarche.dossiers.nodes)
        messages = get_messages(demarche.dossiers.nodes)
        avis = get_avis(demarche.dossiers.nodes)
        releve_index = get_releve_index(demarche.dossiers.nodes)
        volumes_pompes = get_volumes_pompes(demarche.dossiers.nodes)
        extraits_registres = get_extrait_registre(demarche.dossiers.nodes)
        donnees_point_de_prelevement = get_donnees_point_de_prelevement(
            demarche.dossiers.nodes
        )

        donnees_point_de_prelevement_db = [
            DonneesPointDePrelevement(
                id_dossier=dpp.id_dossier,
                ligne=dpp.ligne,
                nom_point_prelevement=dpp.nom_point_prelevement,
                demarche_data_brute_id=demarche_data_brute_id,
                fichiers_tableurs=[
                    PieceJointe(**fichier.dict()) for fichier in dpp.fichiers_tableurs
                ],
                fichiers_autres_documents=[
                    PieceJointe(**fichier.dict())
                    for fichier in dpp.fichiers_autres_documents
                ],
            )
            for dpp in donnees_point_de_prelevement
        ]

        extraits_registres_db = [
            ExtraitDeRegistre(
                id_dossier=er.id_dossier,
                ligne=er.ligne,
                extraits_registres_papiers=[
                    PieceJointe(**fichier.dict())
                    for fichier in er.extraits_registres_papiers
                ],
                demarche_data_brute_id=demarche_data_brute_id,
            )
            for er in extraits_registres
        ]
        volumes_pompes_db = [
            VolumesPompes(**vp.dict(), demarche_data_brute_id=demarche_data_brute_id)
            for vp in volumes_pompes
        ]
        releve_index_db = [
            ReleveIndex(**ri.dict(), demarche_data_brute_id=demarche_data_brute_id)
            for ri in releve_index
        ]
        processed_dossiers_db = [
            PreprocessedDossier(
                **{
                    **ppd.dict(),
                    "demarche_data_brute_id": demarche_data_brute_id,
                    "fichier_tableau_suivi_camion_citerne": [
                        PieceJointe(**fichier.dict())
                        for fichier in ppd.fichier_tableau_suivi_camion_citerne
                    ],
                }
            )
            for ppd in processed_dossiers
        ]
        avis_db = [
            Avis(
                **{
                    **avs.dict(),
                    "demarche_data_brute_id": demarche_data_brute_id,
                    "pieces_jointes": [
                        PieceJointe(**fichier.dict()) for fichier in avs.pieces_jointes
                    ],
                }
            )
            for avs in avis
        ]
        messages_db = [
            Message(
                **{
                    **msg.dict(),
                    "demarche_data_brute_id": demarche_data_brute_id,
                    "pieces_jointes": [
                        PieceJointe(**fichier.dict()) for fichier in msg.pieces_jointes
                    ],
                }
            )
            for msg in messages
        ]

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
                demarche_data_object_storage_key = f"demandes_simplifiees/demarche_data_brute/{hashed_collected_data}__{self.demarche_number}.json"
                upload_file(
                    bucket_name=settings.SCW_S3_BUCKET,
                    key=demarche_data_object_storage_key,
                    body=collected_data,
                )
                new_demarche_data_brute = DemarcheDataBrute(
                    id=demarche_data_brute_id,
                    hashed_collected_data=hashed_collected_data,
                    object_storage_key=demarche_data_object_storage_key,
                    demarche_number=self.demarche_number,
                )
                print("Data is created")
                session.add(new_demarche_data_brute)
                session.commit()
                session.refresh(new_demarche_data_brute)
                new_demarche_data_brute.donnees_point_de_prelevements = (
                    donnees_point_de_prelevement_db
                )
                new_demarche_data_brute.extrait_de_registres = extraits_registres_db
                new_demarche_data_brute.volumes_pompes = volumes_pompes_db
                new_demarche_data_brute.releve_index = releve_index_db
                new_demarche_data_brute.avis = avis_db
                new_demarche_data_brute.message = messages_db
                session.add_all(donnees_point_de_prelevement_db)
                session.add_all(extraits_registres_db)
                session.add_all(volumes_pompes_db)
                session.add_all(releve_index_db)
                session.add_all(processed_dossiers_db)
                session.add_all(avis_db)
                session.add_all(messages_db)
                session.commit()
                print(f"Data collected and saved with id {new_demarche_data_brute.id}")
            except Exception as e:
                print(f"Error while saving data: {e}")
                session.rollback()
                raise e
            finally:
                session.close()

        context["ti"].xcom_push(
            key="demarche_data_brute_id", value=str(demarche_data_brute_id)
        )


class CollectCiterneData(BaseOperator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context):
        demarche_data_brute_id = context["ti"].xcom_pull(key="demarche_data_brute_id")
        with local_session() as session:
            df = pd.DataFrame()
            query = select(PreprocessedDossier).where(
                PreprocessedDossier.demarche_data_brute_id == demarche_data_brute_id
            )
            for result in session.execute(query):
                dossier = result[0]
                if dossier.fichier_tableau_suivi_camion_citerne:
                    for file in dossier.fichier_tableau_suivi_camion_citerne:
                        result = process_standard_v1_file(dossier, file)
                        if result is not None:
                            df = pd.concat([df, result])

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
        with local_session() as session:
            donnees_point_de_prelevement_entries = (
                get_donnees_point_de_prelevement_by_ddb_id(
                    session, demarche_data_brute_id
                )
            )
            if not donnees_point_de_prelevement_entries:
                print("Aucun point de prélèvement trouvé")

            prelevements = []
            for result in donnees_point_de_prelevement_entries:
                current_donnees_point_de_prelevement = result[0]
                dossier_tuple = get_preprocessed_dossier(
                    session,
                    demarche_data_brute_id,
                    current_donnees_point_de_prelevement.id_dossier,
                )
                dossier = dossier_tuple[0] if dossier_tuple else None

                if current_donnees_point_de_prelevement.fichiers_tableurs:
                    for (
                        current_tableur
                    ) in current_donnees_point_de_prelevement.fichiers_tableurs:
                        new_df = process_standard_v2_file(dossier, current_tableur)
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
                                    nom_point_prelevement=x["nom_point_prelevement"],
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
                            prelevements.extend(new_prelevements)
                session.add_all(prelevements)
                session.commit()
