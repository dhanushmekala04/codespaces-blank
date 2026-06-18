from app.repositories.base import BaseRepository
from app.schemas.case import CaseDocument


class CaseRepository(BaseRepository[CaseDocument]):
    def __init__(self):
        super().__init__(collection_name="cases", model_cls=CaseDocument)
