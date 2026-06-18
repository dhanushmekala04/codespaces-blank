from app.repositories.base import BaseRepository
from app.schemas.appointment import AppointmentDocument


class AppointmentRepository(BaseRepository[AppointmentDocument]):
    def __init__(self):
        super().__init__(collection_name="appointments", model_cls=AppointmentDocument)
