"""Timeline API routes — patient event history and root cause queries."""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.services.event_service import EventService

router = APIRouter(prefix="/timeline", tags=["timeline"])
_event_service = EventService()


class TimelineEventItem(BaseModel):
    id: str
    event_type: str
    event_time: str
    entity_type: str
    entity_id: str
    actor_type: str
    metadata: dict


class TimelineResponse(BaseModel):
    patient_id: str
    count: int
    events: list[TimelineEventItem]


@router.get("/{patient_id}", response_model=TimelineResponse)
async def get_patient_timeline(
    patient_id: str,
    limit: int = Query(50, ge=1, le=200, description="Max events to return"),
    event_type: str | None = Query(None, description="Filter by event type"),
) -> TimelineResponse:
    """Get the event timeline for a patient."""
    from app.repositories.event_repository import EventRepository

    repo = EventRepository()

    events = await repo.get_patient_events(
        patient_id=patient_id,
        limit=limit,
        event_type=event_type,
    )

    items = [
        TimelineEventItem(
            id=str(e.id),
            event_type=e.event_type,
            event_time=e.event_time.isoformat() if e.event_time else "",
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            actor_type=e.actor_type,
            metadata=e.metadata,
        )
        for e in events
    ]

    return TimelineResponse(
        patient_id=patient_id,
        count=len(items),
        events=items,
    )


@router.get("/{patient_id}/recent", response_model=TimelineResponse)
async def get_recent_events(
    patient_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
) -> TimelineResponse:
    """Get events from the last N days for a patient."""
    from app.repositories.event_repository import EventRepository

    repo = EventRepository()
    events = await repo.get_recent_events(patient_id=patient_id, days=days)

    items = [
        TimelineEventItem(
            id=str(e.id),
            event_type=e.event_type,
            event_time=e.event_time.isoformat() if e.event_time else "",
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            actor_type=e.actor_type,
            metadata=e.metadata,
        )
        for e in events
    ]

    return TimelineResponse(
        patient_id=patient_id,
        count=len(items),
        events=items,
    )
