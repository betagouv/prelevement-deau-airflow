from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings, case_sensitive=True):
    DATABASE_URL: str
    DEMARCHES_SIMPLIFIEES_URL: str
    DEMARCHES_SIMPLIFIEES_TOKEN: str
    DEMARCHE_ID: int
    INSTRUCTEUR_ID: str
    SCW_ACCESS_KEY: str
    SCW_SECRET_KEY: str
    SCW_DEFAULT_ORGANIZATION_ID: str
    SCW_DEFAULT_PROJECT_ID: str
    SCW_S3_URL: str
    SCW_S3_REGION: str
    SCW_S3_BUCKET: str
    SCW_S3_PUBLIC_BUCKET: str
    DRY_RUN: bool
    TMP_ERROR_MESSAGE_RECEPTION_DOSSIER_ID: str
    TMP_ERROR_MESSAGE_RECEPTION_DEMARCHE_TOKEN: str


settings = Settings()
