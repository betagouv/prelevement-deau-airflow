from airflow.models import BaseOperator
from sqlalchemy import select

from utils.db.init_db import get_local_session
from utils.demarchessimplifiees.data_extractions.models import (
    Avis,
    CiterneReleve,
    DemarcheDataBrute,
    DonneesPointDePrelevement,
    ExtraitDeRegistre,
    Message,
    PrelevementReleve,
    PreprocessedDossier,
    ReleveIndex,
    VolumesPompes,
)
from utils.demarchessimplifiees.last_snapshot.models import (
    AvisAssocLastSnapshot,
    AvisLastSnapshot,
    CiterneReleveLastSnapshot,
    DemarcheDataBruteLastSnapshot,
    DonneesPointDePrelevementLastSnapshot,
    DossierFichierTableauSuiviCamionCiterneAssocLastSnapshot,
    ExtraitDeRegistreLastSnapshot,
    ExtraitsDeRegistresAssocLastSnapshot,
    FichiersAutresDocumentsAssocLastSnapshot,
    FichiersTableursAssocLastSnapshot,
    MessageAssocLastSnapshot,
    MessageLastSnapshot,
    PieceJointeLastSnapshot,
    PrelevementReleveLastSnapshot,
    PreprocessedDossierLastSnapshot,
    ReleveIndexLastSnapshot,
    VolumesPompesLastSnapshot,
)
from utils.demarchessimplifiees.last_snapshot.services import (
    copy_table_to_last_snapshot,
)


class StoreLastSnapshotData(BaseOperator):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context):
        demarche_data_brute_id = context["ti"].xcom_pull(key="demarche_data_brute_id")
        with get_local_session() as session:
            list_of_tables = [
                FichiersTableursAssocLastSnapshot,
                FichiersAutresDocumentsAssocLastSnapshot,
                ExtraitsDeRegistresAssocLastSnapshot,
                MessageAssocLastSnapshot,
                AvisAssocLastSnapshot,
                DossierFichierTableauSuiviCamionCiterneAssocLastSnapshot,
                PieceJointeLastSnapshot,
                DonneesPointDePrelevementLastSnapshot,
                PreprocessedDossierLastSnapshot,
                ReleveIndexLastSnapshot,
                VolumesPompesLastSnapshot,
                ExtraitDeRegistreLastSnapshot,
                AvisLastSnapshot,
                MessageLastSnapshot,
                CiterneReleveLastSnapshot,
                PrelevementReleveLastSnapshot,
                DemarcheDataBruteLastSnapshot,
            ]

            for table in list_of_tables:
                session.query(table).delete()

            session.commit()

            last_demarche_data_brute = session.execute(
                select(DemarcheDataBrute)
                .where(DemarcheDataBrute.id == demarche_data_brute_id)
                .limit(1)
            ).first()[0]

            demarche_data_brut_last_snapshot_data = last_demarche_data_brute.__dict__
            del demarche_data_brut_last_snapshot_data["_sa_instance_state"]
            demarche_data_brut_last_snapshot = DemarcheDataBruteLastSnapshot(
                **demarche_data_brut_last_snapshot_data
            )

            session.add(demarche_data_brut_last_snapshot)
            session.commit()

            copy_table_to_last_snapshot(
                DonneesPointDePrelevement,
                DonneesPointDePrelevementLastSnapshot,
                demarche_data_brute_id,
                session,
            )

            copy_table_to_last_snapshot(
                PreprocessedDossier,
                PreprocessedDossierLastSnapshot,
                demarche_data_brute_id,
                session,
            )

            copy_table_to_last_snapshot(
                ReleveIndex, ReleveIndexLastSnapshot, demarche_data_brute_id, session
            )

            copy_table_to_last_snapshot(
                VolumesPompes,
                VolumesPompesLastSnapshot,
                demarche_data_brute_id,
                session,
            )

            copy_table_to_last_snapshot(
                ExtraitDeRegistre,
                ExtraitDeRegistreLastSnapshot,
                demarche_data_brute_id,
                session,
            )

            copy_table_to_last_snapshot(
                Avis, AvisLastSnapshot, demarche_data_brute_id, session
            )

            copy_table_to_last_snapshot(
                Message, MessageLastSnapshot, demarche_data_brute_id, session
            )

            copy_table_to_last_snapshot(
                CiterneReleve,
                CiterneReleveLastSnapshot,
                demarche_data_brute_id,
                session,
            )

            copy_table_to_last_snapshot(
                PrelevementReleve,
                PrelevementReleveLastSnapshot,
                demarche_data_brute_id,
                session,
            )

            session.commit()
