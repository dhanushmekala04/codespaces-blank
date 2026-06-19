"""Event Repository for event sourcing operations."""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from app.repositories.base import BaseRepository
from app.schemas.event import EventDocument


class EventRepository(BaseRepository[EventDocument]):
    """Repository for event operations and timeline queries."""

    def __init__(self):
        super().__init__(collection_name="events", model_cls=EventDocument)

    async def get_patient_events(
        self,
        patient_id: str,
        limit: int = 50,
        event_type: str | None = None,
    ) -> list[EventDocument]:
        """
        Get events for a patient in chronological order.
        
        Args:
            patient_id: Patient identifier
            limit: Maximum number of events
            event_type: Optional filter by event type
            
        Returns:
            List of events sorted by event_time descending
        """
        collection = await self._collection()
        
        filters: dict[str, Any] = {
            "patient_id": patient_id,
            "is_deleted": False,
        }
        
        if event_type:
            filters["event_type"] = event_type
        
        cursor = collection.find(filters).sort("event_time", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_by_type(
        self,
        patient_id: str,
        event_type: str,
    ) -> list[EventDocument]:
        """Get all events of a specific type for a patient."""
        return await self.get_patient_events(
            patient_id=patient_id,
            event_type=event_type,
            limit=100,
        )

    async def get_events_between(
        self,
        patient_id: str,
        start_time: str,
        end_time: str,
    ) -> list[EventDocument]:
        """
        Get events within a time range.
        
        Args:
            patient_id: Patient identifier
            start_time: ISO format start datetime
            end_time: ISO format end datetime
            
        Returns:
            List of events in the time range
        """
        collection = await self._collection()
        
        filters = {
            "patient_id": patient_id,
            "is_deleted": False,
            "event_time": {
                "$gte": start_time,
                "$lte": end_time,
            },
        }
        
        cursor = collection.find(filters).sort("event_time", 1)
        docs = await cursor.to_list(length=None)
        
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_events_by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list[EventDocument]:
        """Get all events related to a specific entity."""
        collection = await self._collection()
        
        filters = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "is_deleted": False,
        }
        
        cursor = collection.find(filters).sort("event_time", 1)
        docs = await cursor.to_list(length=None)
        
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_recent_events(
        self,
        patient_id: str,
        days: int = 30,
    ) -> list[EventDocument]:
        """Get events from the last N days."""
        from datetime import datetime, timedelta, timezone
        
        start_time = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        end_time = datetime.now(timezone.utc).isoformat()
        
        return await self.get_events_between(patient_id, start_time, end_time)

    async def count_events_by_type(
        self,
        patient_id: str,
        event_type: str,
    ) -> int:
        """Count events of a specific type."""
        collection = await self._collection()
        
        return await collection.count_documents({
            "patient_id": patient_id,
            "event_type": event_type,
            "is_deleted": False,
        })

    async def get_latest_event(
        self,
        patient_id: str,
        event_type: str | None = None,
    ) -> EventDocument | None:
        """Get the most recent event for a patient."""
        events = await self.get_patient_events(
            patient_id=patient_id,
            event_type=event_type,
            limit=1,
        )
        
        return events[0] if events else None
