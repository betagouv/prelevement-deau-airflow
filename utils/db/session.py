from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.core.settings import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
