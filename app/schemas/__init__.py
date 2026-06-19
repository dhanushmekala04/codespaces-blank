from app.schemas.base import BaseDocument, TimestampedModel
from app.schemas.enums import (
    AppointmentStatus,
    BillingStatus,
    CaseStatus,
    ClaimStatus,
    ConsentStatus,
    EventType,
    InsuranceStatus,
    MedicationStatus,
    PatientStatus,
    ProviderRole,
    RefillsStatus,
)
from app.schemas.patient import PatientDocument, PatientCreate, PatientUpdate
from app.schemas.appointment import AppointmentDocument, AppointmentCreate, AppointmentUpdate
from app.schemas.billing import BillingDocument, BillingCreate, BillingUpdate
from app.schemas.insurance import InsuranceDocument, InsuranceCreate, InsuranceUpdate, ClaimDocument
from app.schemas.case import CaseDocument, CaseCreate, CaseUpdate
from app.schemas.event import EventDocument, EventCreate, EventUpdate, EventTypes
from app.schemas.audit import AuditLogDocument, AuditLogCreate
from app.schemas.conversation import ConversationHistoryDocument, ConversationHistoryCreate

__all__ = [
    # Base
    "BaseDocument",
    "TimestampedModel",
    # Enums
    "AppointmentStatus",
    "BillingStatus",
    "CaseStatus",
    "ClaimStatus",
    "ConsentStatus",
    "EventType",
    "InsuranceStatus",
    "MedicationStatus",
    "PatientStatus",
    "ProviderRole",
    "RefillsStatus",
    # Patient
    "PatientDocument",
    "PatientCreate",
    "PatientUpdate",
    # Appointment
    "AppointmentDocument",
    "AppointmentCreate",
    "AppointmentUpdate",
    # Billing
    "BillingDocument",
    "BillingCreate",
    "BillingUpdate",
    # Insurance
    "InsuranceDocument",
    "InsuranceCreate",
    "InsuranceUpdate",
    "ClaimDocument",
    # Case
    "CaseDocument",
    "CaseCreate",
    "CaseUpdate",
    # Event
    "EventDocument",
    "EventCreate",
    "EventUpdate",
    "EventTypes",
    # Audit
    "AuditLogDocument",
    "AuditLogCreate",
    # Conversation
    "ConversationHistoryDocument",
    "ConversationHistoryCreate",
]
