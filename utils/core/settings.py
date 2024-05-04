from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings, case_sensitive=True):
    DATABASE_URL: str
    DEMARCHES_SIMPLIFIEES_URL: str
    DEMARCHES_SIMPLIFIEES_TOKEN: str


settings = Settings()
