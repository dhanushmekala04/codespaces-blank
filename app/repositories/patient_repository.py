from app.repositories.base import BaseRepository
from app.schemas.patient import PatientDocument


class PatientRepository(BaseRepository[PatientDocument]):
    def __init__(self):
        super().__init__(collection_name="patients", model_cls=PatientDocument)
