import numpy as np
from sqlalchemy import text

from utils.common.object_storage_client import load_csv_from_s3
from utils.common.utils import dataframe_to_sqlalchemy_objects
from utils.core.settings import settings
from utils.db.init_db import get_local_session
from utils.donnees_historiques.models import (
    CREATE_FUNCTION_NETTOYAGE_VALEURS_NULL_ET_ESPACE,
    CREATE_VIEW_JDD_ANALYSE,
    DROP_JDD_ANALYSE_CASCADE,
    DROP_RESULTAT_SUIVI_CASCADE,
    Bss,
    BvBdCarthage,
    Commune,
    Document,
    HistoricalDBBase,
    JddAnalyse,
    LienDocumentPointPrelevement,
    MeContinentalesBV,
    Meso,
    Nomenclature,
    OuvrageBNPE,
    PointPrelevement,
    PointPrelevementBNPE,
    PrelevementBNPE,
    Regle,
    ResultatSuivi,
    ResultatSuiviPourImport,
    SerieDonnees,
    SerieDonneesPourImport,
)

historical_db_tables = [
    ResultatSuivi,
    SerieDonnees,
    Regle,
    LienDocumentPointPrelevement,
    PointPrelevement,
    JddAnalyse,
    Meso,
    BvBdCarthage,
    MeContinentalesBV,
    Nomenclature,
    PrelevementBNPE,
    SerieDonneesPourImport,
    ResultatSuiviPourImport,
    Document,
    Commune,
    Bss,
    PointPrelevementBNPE,
    OuvrageBNPE,
]


def create_historical_db_schemas(db_url=settings.HISTORICAL_DATABASE_URL):
    with get_local_session(db_url) as session:
        session.execute(text("CREATE schema IF NOT EXISTS prelevement ;"))
        session.execute(text("CREATE schema IF NOT EXISTS bnpe ;"))
        session.execute(text("CREATE schema IF NOT EXISTS referentiel ;"))
        session.execute(text("CREATE schema IF NOT EXISTS donnee_brute ;"))
        session.execute(text("CREATE schema IF NOT EXISTS demarches_simplifiees ;"))
        session.commit()


def post_processing():
    with get_local_session(settings.HISTORICAL_DATABASE_URL) as session:
        session.execute(text(CREATE_VIEW_JDD_ANALYSE))
        session.execute(text(CREATE_FUNCTION_NETTOYAGE_VALEURS_NULL_ET_ESPACE))

        session.execute(
            text(
                "COMMENT ON SCHEMA prelevement IS 'Schéma stockant les tables liées au suivi des points de prélèvement sur le périmètre géographique sur lequel porte la base de données. Il s''agit du schéma central de la base de données';"
            )
        )
        session.execute(
            text(
                "COMMENT ON SCHEMA bnpe IS 'Schéma stockant les tables issues de la Banque nationale des données sur les prélèvements d''eau (BNPE - https://bnpe.eaufrance.fr/)';"
            )
        )
        session.execute(
            text(
                "COMMENT ON SCHEMA referentiel IS 'Schéma stockant les divers référentiels, notamment cartographiques, locaux ou nationaux, en lien avec la question des prélèvements (masses d''eau, communes, BSS...)';"
            )
        )
        session.execute(
            text(
                "COMMENT ON SCHEMA donnee_brute IS 'Schéma stockant les données brutes avant intégration dans les différentes tables standardisées de la base de données. Ces données sont issues d''import manuel de fichiers csv par l''administrateur régional';"
            )
        )
        session.execute(
            text(
                "COMMENT ON SCHEMA demarches_simplifiees IS 'Schéma stockant les données saisies par les préleveurs ou leurs ayants droits sur demarches-simplifiées';"
            )
        )

        session.execute(
            text(
                "COMMENT ON VIEW public.v_jdd_analyse IS 'Vue permettant de visualiser de manière lisible et agrégée les listes de valeur par champ pour les tables dont l analyse a été réalisée';"
            )
        )
        session.commit()


def drop_table_with_cascade(engine, db_url=settings.HISTORICAL_DATABASE_URL):
    with get_local_session(db_url) as session:
        session.execute(text(DROP_JDD_ANALYSE_CASCADE))
        session.execute(text(DROP_RESULTAT_SUIVI_CASCADE))
        session.commit()

        HistoricalDBBase.metadata.drop_all(engine)


def install_extension_postgis(db_url=settings.HISTORICAL_DATABASE_URL):
    with get_local_session(db_url) as session:
        session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        session.commit()


def load_historical_data():
    with get_local_session(settings.HISTORICAL_DATABASE_URL) as session:
        # BSS
        bss_df = load_csv_from_s3("donnees_source/referentiel/BSS/BSS.csv")
        bss_df["code_bss_ancien"] = bss_df["indice"].astype(str) + bss_df[
            "designation"
        ].fillna("").apply(lambda x: "/" + x if x else "")
        bss_objects = dataframe_to_sqlalchemy_objects(bss_df, Bss)

        # Commune
        commune_df = load_csv_from_s3("donnees_source/referentiel/commune/commune.csv")
        commune_objects = dataframe_to_sqlalchemy_objects(commune_df, Commune)

        # MESO
        meso_df = load_csv_from_s3("donnees_source/referentiel/meso/meso.csv", sep=",")
        meso_objects = dataframe_to_sqlalchemy_objects(meso_df, Meso)
        # Mise à jour de la colonne geom avec st_geomfromtext
        for meso in meso_objects:
            wkt = meso_df.loc[meso_df["code"] == meso.code, "wkt"].values[0]
            meso.geom = session.execute(
                text("SELECT ST_GeomFromText(:wkt)"), {"wkt": wkt}
            ).scalar()

        # BvBdCarthage
        bv_bd_carthage_df = load_csv_from_s3(
            "donnees_source/referentiel/bv_bdcarthage/bv_bdcarthage.csv", sep=","
        )
        bv_bd_carthage_objects = dataframe_to_sqlalchemy_objects(
            bv_bd_carthage_df, BvBdCarthage
        )
        for bv_bd_carthage in bv_bd_carthage_objects:
            wkt = bv_bd_carthage_df.loc[
                bv_bd_carthage_df["code_cours"] == bv_bd_carthage.code_cours, "wkt"
            ].values[0]
            bv_bd_carthage.geom = session.execute(
                text("SELECT ST_GeomFromText(:wkt)"), {"wkt": wkt}
            ).scalar()

        # MeContinentalesBV
        me_continentales_bv_df = load_csv_from_s3(
            "donnees_source/referentiel/me_continentales_bv/bv_me_continentales.csv",
            sep=",",
        )
        me_continentales_bv_objects = dataframe_to_sqlalchemy_objects(
            me_continentales_bv_df, MeContinentalesBV
        )
        for me_continentales_bv in me_continentales_bv_objects:
            wkt = me_continentales_bv_df.loc[
                me_continentales_bv_df["code_dce"] == me_continentales_bv.code_dce,
                "wkt",
            ].values[0]
            me_continentales_bv.geom = session.execute(
                text("SELECT ST_GeomFromText(:wkt)"), {"wkt": wkt}
            ).scalar()

        # Nomenclature
        nomenclature_df = load_csv_from_s3(
            "donnees_source/referentiel/nomenclature/nomenclature.csv", sep=","
        )
        nomenclature_objects = dataframe_to_sqlalchemy_objects(
            nomenclature_df, Nomenclature
        )

        # OuvrageBNPE
        ouvrage_bnpe_df = load_csv_from_s3("donnees_source/bnpe/ouvrage.csv")
        ouvrage_bnpe_objects = dataframe_to_sqlalchemy_objects(
            ouvrage_bnpe_df, OuvrageBNPE
        )

        # PointPrelevementBNPE
        point_prelevement_bnpe_df = load_csv_from_s3(
            "donnees_source/bnpe/points_prelevements.csv"
        )
        point_prelevement_bnpe_objects = dataframe_to_sqlalchemy_objects(
            point_prelevement_bnpe_df, PointPrelevementBNPE
        )

        # PrelevementBNPE
        prelevement_bnpe_df = load_csv_from_s3(
            "donnees_source/bnpe/prelevements.csv", sep=","
        )
        prelevement_bnpe_objects = dataframe_to_sqlalchemy_objects(
            prelevement_bnpe_df, PrelevementBNPE
        )

        # SerieDonneesPourImport
        serie_donnees_pour_import_df = load_csv_from_s3(
            "donnees_source/prelevement/serie_donnees.csv", sep=","
        )
        serie_donnees_pour_import_df = serie_donnees_pour_import_df.replace(
            np.NaN, None
        )
        serie_donnees_pour_import_objects = dataframe_to_sqlalchemy_objects(
            serie_donnees_pour_import_df, SerieDonneesPourImport
        )

        # ResultatSuiviPourImport
        resultat_suivi_pour_import_df = load_csv_from_s3(
            "donnees_source/prelevement/resultat_suivi.csv", sep=","
        )
        resultat_suivi_pour_import_df = resultat_suivi_pour_import_df.replace(
            np.NaN, None
        )
        resultat_suivi_pour_import_objects = dataframe_to_sqlalchemy_objects(
            resultat_suivi_pour_import_df, ResultatSuiviPourImport
        )

        # PointPrelevement
        point_prelevement_df = load_csv_from_s3(
            "donnees_source/prelevement/point_prelevement.csv", sep=","
        )
        point_prelevement_df = point_prelevement_df.replace(np.NaN, None)
        point_prelevement_objects = dataframe_to_sqlalchemy_objects(
            point_prelevement_df, PointPrelevement
        )

        # Document
        document_df = load_csv_from_s3(
            "donnees_source/prelevement/document.csv", sep=","
        )
        document_df = document_df.replace(np.NaN, None)
        document_objects = dataframe_to_sqlalchemy_objects(document_df, Document)

        # LienDocumentPointPrelevement
        lien_document_point_prelevement_df = load_csv_from_s3(
            "donnees_source/prelevement/lien_document_point_prelevement.csv", sep=","
        )
        lien_document_point_prelevement_df = lien_document_point_prelevement_df.replace(
            np.NaN, None
        )
        lien_document_point_prelevement_objects = dataframe_to_sqlalchemy_objects(
            lien_document_point_prelevement_df, LienDocumentPointPrelevement
        )

        # Règle
        regle_df = load_csv_from_s3("donnees_source/prelevement/regle.csv", sep=",")
        regle_df = regle_df.replace(np.NaN, None)
        regle_objects = dataframe_to_sqlalchemy_objects(regle_df, Regle)

        # SerieDonnees
        serie_donnees_df = load_csv_from_s3(
            "donnees_source/prelevement/processed_serie_donnees.csv", sep=","
        )
        serie_donnees_df = serie_donnees_df.replace(np.NaN, None)
        serie_donnees_objects = dataframe_to_sqlalchemy_objects(
            serie_donnees_df, SerieDonnees
        )

        # ResultatSuivi
        resultat_suivi_df = load_csv_from_s3(
            "donnees_source/prelevement/processed_resultat_suivi.csv", sep=","
        )
        resultat_suivi_df = resultat_suivi_df.replace(np.NaN, None)
        resultat_suivi_objects = dataframe_to_sqlalchemy_objects(
            resultat_suivi_df, ResultatSuivi
        )

        session.bulk_save_objects(bss_objects)
        session.bulk_save_objects(commune_objects)
        session.bulk_save_objects(meso_objects)
        session.bulk_save_objects(bv_bd_carthage_objects)
        session.bulk_save_objects(me_continentales_bv_objects)
        session.bulk_save_objects(nomenclature_objects)
        session.bulk_save_objects(ouvrage_bnpe_objects)
        session.bulk_save_objects(point_prelevement_bnpe_objects)
        session.bulk_save_objects(prelevement_bnpe_objects)
        session.bulk_save_objects(serie_donnees_pour_import_objects)
        session.bulk_save_objects(resultat_suivi_pour_import_objects)
        session.bulk_save_objects(point_prelevement_objects)
        session.bulk_save_objects(document_objects)
        session.bulk_save_objects(lien_document_point_prelevement_objects)
        session.bulk_save_objects(regle_objects)
        session.bulk_save_objects(serie_donnees_objects)
        session.bulk_save_objects(resultat_suivi_objects)
        session.commit()
