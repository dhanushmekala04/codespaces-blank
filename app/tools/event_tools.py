"""Event tools — callable by agents for timeline and root cause analysis."""

from app.services.event_service import EventService

event_service = EventService()


async def get_patient_timeline(patient_id: str, limit: int = 50) -> dict:
    """Get the patient event timeline in reverse-chronological order."""
    events = await event_service.get_patient_timeline(patient_id, limit=limit)
    return {
        "patient_id": patient_id,
        "count": len(events),
        "events": events,
    }


async def get_events_by_type(patient_id: str, event_type: str) -> dict:
    """Get all events of a specific type for a patient."""
    events = await event_service.get_events_by_type(patient_id, event_type)
    return {
        "patient_id": patient_id,
        "event_type": event_type,
        "count": len(events),
        "events": [
            {
                "_id": str(e.id),
                "event_type": e.event_type,
                "event_time": e.event_time.isoformat() if e.event_time else "",
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "actor_type": e.actor_type,
                "metadata": e.metadata,
            }
            for e in events
        ],
    }


async def get_root_cause(patient_id: str) -> dict:
    """
    Surface root cause analysis hints from recent events.

    The EventInvestigationAgent performs the deep Nemotron-powered analysis;
    this tool provides the raw event data to support that investigation.
    """
    events = await event_service.get_patient_timeline(patient_id, limit=50)
    return {
        "patient_id": patient_id,
        "event_count": len(events),
        "recent_events": events[:10],
        "note": "Root cause analysis is performed by the EventInvestigationAgent using these events.",
    }
