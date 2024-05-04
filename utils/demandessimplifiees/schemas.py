from pydantic import BaseModel


class DemarcheDataBruteIn(BaseModel):
    hashed_collected_data: str
    file_path: str
    demarche_number: int

    class Config:
        from_attributes = True
