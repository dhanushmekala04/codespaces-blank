"""Event schema for event sourcing and Patient 360 timeline."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.schemas.base import BaseDocument


ActorType = Literal["patient", "provider", "staff", "system", "insurance", "agent"]
EntityType = Literal[
    "appointment",
    "claim",
    "billing",
    "payment",
    "refill",
    "prescription",
    "case",
    "lab",
    "procedure",
    "document",
    "insurance",
]


class EventDocument(BaseDocument):
    """
    Immutable event record for event sourcing.
    Every business action generates an event.
    """

    event_id: str = Field(default="", description="Unique event identifier")
    patient_id: str = Field(..., description="Patient reference")

    entity_type: EntityType = Field(..., description="Type of business entity")
    entity_id: str = Field(..., description="Entity identifier")

    event_type: str = Field(..., description="Event name (e.g., claim_denied)")
    event_time: datetime = Field(..., description="When the event occurred")

    actor_type: ActorType = Field(default="system", description="Who performed the action")
    actor_id: str = Field(default="system", description="Actor identifier")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Event-specific data")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "_id": "EVT001",
                "event_id": "EVT001",
                "patient_id": "PAT001",
                "entity_type": "claim",
                "entity_id": "CLM001",
                "event_type": "claim_denied",
                "event_time": "2026-06-19T10:30:00Z",
                "actor_type": "system",
                "actor_id": "SYSTEM",
                "metadata": {
                    "reason": "Missing Authorization",
                    "claim_amount": 500.00,
                },
            }
        },
    }


class EventCreate(EventDocument):
    """Schema for creating a new event."""
    pass


class EventUpdate(BaseDocument):
    """Schema for updating event metadata (events are mostly immutable)."""
    metadata: dict[str, Any] | None = None


# Common event types
class EventTypes:
    """Standard event type constants."""

    # Appointment events
    APPOINTMENT_CREATED = "appointment_created"
    APPOINTMENT_RESCHEDULED = "appointment_rescheduled"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_COMPLETED = "appointment_completed"
    APPOINTMENT_NO_SHOW = "appointment_no_show"

    # Lab events
    LAB_ORDERED = "lab_ordered"
    LAB_COMPLETED = "lab_completed"
    LAB_CANCELLED = "lab_cancelled"

    # Procedure events
    PROCEDURE_SCHEDULED = "procedure_scheduled"
    PROCEDURE_COMPLETED = "procedure_completed"
    PROCEDURE_CANCELLED = "procedure_cancelled"

    # Billing events
    CHARGE_ADDED = "charge_added"
    PAYMENT_RECEIVED = "payment_received"
    BALANCE_ADJUSTED = "balance_adjusted"
    REFUND_ISSUED = "refund_issued"

    # Claim events
    CLAIM_CREATED = "claim_created"
    CLAIM_SUBMITTED = "claim_submitted"
    CLAIM_APPROVED = "claim_approved"
    CLAIM_DENIED = "claim_denied"
    CLAIM_PENDING = "claim_pending"
    CLAIM_PAID = "claim_paid"

    # Refill events
    REFILL_REQUESTED = "refill_requested"
    REFILL_APPROVED = "refill_approved"
    REFILL_REJECTED = "refill_rejected"
    REFILL_COMPLETED = "refill_completed"

    # Case events
    CASE_OPENED = "case_opened"
    CASE_UPDATED = "case_updated"
    CASE_CLOSED = "case_closed"

    # Document events
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_REVIEWED = "document_reviewed"
    DOCUMENT_SIGNED = "document_signed"

    # Insurance events
    INSURANCE_VERIFIED = "insurance_verified"
    INSURANCE_EXPIRED = "insurance_expired"
    COVERAGE_CHANGED = "coverage_changed"

    # Authorization events
    AUTHORIZATION_REQUESTED = "authorization_requested"
    AUTHORIZATION_APPROVED = "authorization_approved"
    AUTHORIZATION_DENIED = "authorization_denied"
