from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.core.settings import settings


@contextmanager
def get_local_session(url: str = settings.DATABASE_URL):
    engine = create_engine(url, pool_pre_ping=True)
    local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = local_session()
    try:
        yield db
    finally:
        db.close()
