from app.repositories.base import BaseRepository
from app.schemas.insurance import InsuranceDocument


class InsuranceRepository(BaseRepository[InsuranceDocument]):
    def __init__(self):
        super().__init__(collection_name="insurance", model_cls=InsuranceDocument)
