from airflow.models import BaseOperator
from sqlalchemy import create_engine, text

from utils.core.settings import settings
from utils.db.init_db import get_local_session
from utils.demarchessimplifiees.last_snapshot.models import (
    AvisAssocLastSnapshot,
    AvisLastSnapshot,
    Base,
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


class MergeLastSnapshotOperator(BaseOperator):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context):
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

        # Create an engine for the target database
        engine = create_engine(settings.MERGED_DATABASE_URL, pool_pre_ping=True)

        engine.execute(
            text("CREATE schema IF NOT EXISTS demarches_simplifiees_last_snapshot ;")
        )

        # Delete tables in the target database
        Base.metadata.drop_all(engine)

        # Create tables in the target database if they do not exist
        Base.metadata.create_all(engine)

        # Copy data from source to target
        with get_local_session(
            settings.DATABASE_URL
        ) as source_session, get_local_session(
            settings.MERGED_DATABASE_URL
        ) as target_session:
            for table in reversed(list_of_tables):
                # Fetch data from source table
                data = source_session.query(table).all()

                # Copy data to target table
                for row in data:
                    target_session.merge(row)

                target_session.commit()
