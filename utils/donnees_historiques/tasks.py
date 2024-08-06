from airflow.models import BaseOperator
from sqlalchemy import create_engine

from utils.core.settings import settings
from utils.db.init_db import get_local_session
from utils.donnees_historiques.models import HistoricalDBBase
from utils.donnees_historiques.services import (
    create_historical_db_schemas,
    drop_table_with_cascade,
    historical_db_tables,
    install_extension_postgis,
    load_historical_data,
    post_processing,
)


class LoadHistoricalDataOperator(BaseOperator):

    def execute(self, context):
        engine = create_engine(settings.HISTORICAL_DATABASE_URL, pool_pre_ping=True)
        install_extension_postgis()
        create_historical_db_schemas()

        # Pour supprimer la table avec CASCADE
        drop_table_with_cascade(engine)

        # Pour créer la table
        HistoricalDBBase.metadata.create_all(engine)

        # Créer la vue et ajouter des commentaires
        post_processing()

        load_historical_data()


class MergeHistoricalDBOperator(BaseOperator):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context):
        create_historical_db_schemas(settings.MERGED_DATABASE_URL)
        install_extension_postgis(settings.MERGED_DATABASE_URL)

        # Create an engine for the target database
        engine = create_engine(settings.MERGED_DATABASE_URL, pool_pre_ping=True)

        # Delete tables in the target database
        drop_table_with_cascade(engine, settings.MERGED_DATABASE_URL)

        # Create tables in the target database if they do not exist
        HistoricalDBBase.metadata.create_all(engine)

        # Copy data from source to target
        with get_local_session(
            settings.HISTORICAL_DATABASE_URL
        ) as source_session, get_local_session(
            settings.MERGED_DATABASE_URL
        ) as target_session:
            pass
            for table in reversed(historical_db_tables):
                # Fetch data from source table
                data = source_session.query(table).all()

                # Copy data to target table
                for row in data:
                    target_session.merge(row)

                target_session.commit()
