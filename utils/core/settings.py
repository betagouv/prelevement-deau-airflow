from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings, case_sensitive=True):
    DATABASE_URL: str
    HISTORICAL_DATABASE_URL: str
    MERGED_DATABASE_URL: str
    DEMARCHES_SIMPLIFIEES_URL: str
    DEMARCHES_SIMPLIFIEES_TOKEN: str
    DEMARCHE_ID: int
    SCW_ACCESS_KEY: str
    SCW_SECRET_KEY: str
    SCW_DEFAULT_ORGANIZATION_ID: str
    SCW_DEFAULT_PROJECT_ID: str
    SCW_S3_URL: str
    SCW_S3_REGION: str
    SCW_S3_BUCKET: str


settings = Settings()
