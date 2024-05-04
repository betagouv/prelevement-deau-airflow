from sqlalchemy import Column, Integer, String

from utils.db.base_class import Base


class DemarcheDataBrute(Base):
    __tablename__ = "demarche_data_brute"
    hashed_collected_data = Column(String, unique=True)
    file_path = Column(String, unique=True)
    demarche_number = Column(Integer)
