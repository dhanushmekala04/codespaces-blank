from app.repositories.event_repository import EventRepository
from app.schemas.event import EventDocument


class EventService:
    def __init__(self, event_repository: EventRepository | None = None):
        self.event_repository = event_repository or EventRepository()

    async def list_events(self, patient_id: str) -> list[EventDocument]:
        return await self.event_repository.list({"patient_id": patient_id})
