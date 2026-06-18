from enum import Enum


class PatientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ConsentStatus(str, Enum):
    GRANTED = "granted"
    REVOKED = "revoked"
    PENDING = "pending"


class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class BillingStatus(str, Enum):
    OPEN = "open"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"


class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class InsuranceStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"


class CaseStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    IN_REVIEW = "in_review"


class EventType(str, Enum):
    APPOINTMENT_CREATED = "appointment_created"
    APPOINTMENT_RESCHEDULED = "appointment_rescheduled"
    BILL_CHARGED = "bill_charged"
    PAYMENT_RECEIVED = "payment_received"
    CLAIM_UPDATED = "claim_updated"
    LAB_RESULT_RECEIVED = "lab_result_received"


class MedicationStatus(str, Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    ON_HOLD = "on_hold"


class RefillsStatus(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    DENIED = "denied"
    COMPLETED = "completed"


class ProviderRole(str, Enum):
    PHYSICIAN = "physician"
    NURSE = "nurse"
    ADMIN = "admin"
    SPECIALIST = "specialist"
