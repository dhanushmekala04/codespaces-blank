"""Event Service for managing patient events and timeline."""

from app.repositories.event_repository import EventRepository
from app.schemas.event import EventDocument
from app.services.cache_service import cache_service


class EventService:
    """Service for event operations and timeline generation."""

    def __init__(self, event_repository: EventRepository | None = None):
        self.event_repository = event_repository or EventRepository()

    async def get_patient_timeline(
        self,
        patient_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """
        Get patient timeline events in chronological order.
        Redis cache: timeline:{patient_id}  TTL 5 min
        """
        # Try cache first (only for default limit)
        if limit == 50:
            cached = await cache_service.get_timeline(patient_id)
            if cached is not None:
                return cached

        events = await self.event_repository.get_patient_events(
            patient_id=patient_id,
            limit=limit,
        )

        result = [
            {
                "_id": str(event.id),
                "event_type": event.event_type,
                "event_time": event.event_time.isoformat() if event.event_time else "",
                "actor_type": event.actor_type,
                "metadata": event.metadata,
            }
            for event in events
        ]

        # Cache only the default-limit result
        if limit == 50:
            await cache_service.set_timeline(patient_id, result)

        return result

    async def create_event(
        self,
        patient_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        actor_type: str = "system",
        actor_id: str = "system",
        metadata: dict | None = None,
    ) -> EventDocument:
        """Create a new event."""
        from datetime import datetime, timezone
        from app.schemas.event import EventDocument
        
        event = EventDocument(
            patient_id=patient_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            event_time=datetime.now(timezone.utc),
            actor_type=actor_type,
            actor_id=actor_id,
            metadata=metadata or {},
        )
        
        return await self.event_repository.create(event)

    async def get_events_by_type(
        self,
        patient_id: str,
        event_type: str,
    ) -> list[EventDocument]:
        """Get events of a specific type for a patient."""
        return await self.event_repository.get_by_type(patient_id, event_type)
