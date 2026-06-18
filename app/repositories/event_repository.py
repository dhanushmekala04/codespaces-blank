from app.repositories.base import BaseRepository
from app.schemas.event import EventDocument


class EventRepository(BaseRepository[EventDocument]):
    def __init__(self):
        super().__init__(collection_name="events", model_cls=EventDocument)
