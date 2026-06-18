# EVENT_MODEL.md

# PatientCare Platform Event Model

## Overview

The PatientCare Platform follows an Event-Driven Architecture.

Every meaningful business action generates an immutable event.

Events are the foundation for:

* Patient 360 Timeline
* Event Investigation
* Root Cause Analysis
* Case Summarization
* Auditability
* Explainability
* Historical Reconstruction

---

# Why Event Sourcing?

Traditional systems only store current state.

Example:

```text
Claim Status = Denied
```

This tells us what happened.

It does not tell us:

* Why it happened
* When it happened
* What caused it
* Who performed the action

Event sourcing preserves the complete history.

---

# Core Principle

Every business action becomes an event.

Example:

```text
Appointment Created
       ↓
Appointment Completed
       ↓
Lab Ordered
       ↓
Lab Completed
       ↓
Procedure Completed
       ↓
Charge Added
       ↓
Claim Submitted
       ↓
Claim Denied
```

This chain enables explainability.

---

# Event Collection

MongoDB Collection:

```text
events
```

---

# Base Event Schema

```json
{
  "_id": "EVT001",

  "event_id": "EVT001",

  "patient_id": "PAT001",

  "entity_type": "claim",

  "entity_id": "CLM001",

  "event_type": "claim_denied",

  "event_time": "2026-06-15T10:00:00Z",

  "actor_type": "system",

  "actor_id": "SYSTEM",

  "metadata": {},

  "created_at": "2026-06-15T10:00:00Z"
}
```

---

# Required Event Fields

| Field       | Description                |
| ----------- | -------------------------- |
| event_id    | Unique event identifier    |
| patient_id  | Patient reference          |
| entity_type | Business entity            |
| entity_id   | Entity identifier          |
| event_type  | Event name                 |
| event_time  | Event timestamp            |
| actor_type  | Who performed action       |
| actor_id    | Actor identifier           |
| metadata    | Event-specific information |

---

# Actor Types

```text
patient
provider
staff
system
insurance
agent
```

Example:

```json
{
  "actor_type": "patient",
  "actor_id": "PAT001"
}
```

---

# Entity Types

```text
appointment
claim
billing
payment
refill
prescription
case
lab
procedure
document
insurance
```

---

# Appointment Events

## appointment_created

```json
{
  "event_type": "appointment_created",
  "entity_type": "appointment",
  "entity_id": "APT001"
}
```

---

## appointment_rescheduled

```json
{
  "event_type": "appointment_rescheduled",
  "metadata": {
    "old_date": "2026-06-10",
    "new_date": "2026-06-15"
  }
}
```

---

## appointment_cancelled

```json
{
  "event_type": "appointment_cancelled"
}
```

---

## appointment_completed

```json
{
  "event_type": "appointment_completed"
}
```

---

# Lab Events

## lab_ordered

```json
{
  "event_type": "lab_ordered",
  "metadata": {
    "lab_name": "CBC"
  }
}
```

---

## lab_completed

```json
{
  "event_type": "lab_completed"
}
```

---

# Procedure Events

## procedure_scheduled

```json
{
  "event_type": "procedure_scheduled"
}
```

---

## procedure_completed

```json
{
  "event_type": "procedure_completed"
}
```

---

# Billing Events

## charge_added

```json
{
  "event_type": "charge_added",
  "metadata": {
    "amount": 250,
    "description": "MRI Charge"
  }
}
```

---

## payment_received

```json
{
  "event_type": "payment_received",
  "metadata": {
    "amount": 100
  }
}
```

---

## balance_adjusted

```json
{
  "event_type": "balance_adjusted"
}
```

---

# Claim Events

## claim_created

```json
{
  "event_type": "claim_created"
}
```

---

## claim_submitted

```json
{
  "event_type": "claim_submitted"
}
```

---

## claim_approved

```json
{
  "event_type": "claim_approved"
}
```

---

## claim_denied

```json
{
  "event_type": "claim_denied",
  "metadata": {
    "reason": "Missing Authorization"
  }
}
```

---

# Refill Events

## refill_requested

```json
{
  "event_type": "refill_requested"
}
```

---

## refill_approved

```json
{
  "event_type": "refill_approved"
}
```

---

## refill_rejected

```json
{
  "event_type": "refill_rejected"
}
```

---

# Case Events

## case_opened

```json
{
  "event_type": "case_opened"
}
```

---

## case_updated

```json
{
  "event_type": "case_updated"
}
```

---

## case_closed

```json
{
  "event_type": "case_closed"
}
```

---

# Clinical Document Events

## document_uploaded

```json
{
  "event_type": "document_uploaded"
}
```

---

## document_reviewed

```json
{
  "event_type": "document_reviewed"
}
```

---

# Timeline Generation

Patient timelines are generated directly from events.

Query:

```python
events.find(
    {"patient_id": patient_id}
).sort("event_time", 1)
```

---

# Timeline Example

```text
June 1
Appointment Created

June 5
Appointment Completed

June 5
Lab Ordered

June 7
Lab Completed

June 8
Procedure Completed

June 9
Charge Added

June 10
Claim Submitted

June 12
Claim Denied
```

---

# Event Correlation

Events rarely exist in isolation.

Related events should be connected.

Example:

```text
Appointment Completed
        ↓
Lab Ordered
        ↓
Lab Completed
        ↓
Charge Added
```

This creates a causal chain.

---

# Event Correlation Rules

## Billing Investigation

Search:

```text
charge_added

procedure_completed

lab_completed

payment_received
```

---

## Claim Investigation

Search:

```text
claim_created

claim_submitted

claim_denied

claim_approved
```

---

## Appointment Investigation

Search:

```text
appointment_created

appointment_rescheduled

appointment_cancelled
```

---

# Root Cause Analysis

The Event Investigation Agent uses event chronology.

Process:

```text
Target Event
      ↓
Locate Previous Events
      ↓
Identify Causal Chain
      ↓
Gather Evidence
      ↓
Generate Explanation
```

---

# Example 1

Question:

```text
Why did my bill increase?
```

Timeline:

```text
Appointment Completed
      ↓
Lab Ordered
      ↓
Lab Completed
      ↓
Charge Added
```

Root Cause:

```text
Laboratory services generated an additional charge.
```

---

# Example 2

Question:

```text
Why was my claim denied?
```

Timeline:

```text
Procedure Completed
      ↓
Claim Submitted
      ↓
Claim Denied
```

Metadata:

```text
Missing Authorization
```

Root Cause:

```text
The claim was denied because prior authorization was missing.
```

---

# Event Investigation Output

```json
{
  "root_cause": "Prior authorization was missing before claim submission.",

  "evidence": [
    "Claim Submitted",
    "Claim Denied"
  ],

  "timeline_summary": "Authorization requirement was not completed before claim submission.",

  "confidence": 0.97
}
```

---

# Patient 360 Timeline Model

Patient 360 combines:

```text
Events
Appointments
Claims
Billing
Payments
Cases
Refills
Documents
```

into a unified timeline.

---

# Timeline API Output

```json
{
  "patient_id": "PAT001",

  "timeline": [
    {
      "event_type": "appointment_completed",
      "timestamp": "2026-06-05"
    },
    {
      "event_type": "lab_ordered",
      "timestamp": "2026-06-05"
    }
  ]
}
```

---

# Event Retention Policy

Events should never be deleted.

Events are immutable.

Allowed operations:

```text
CREATE
READ
```

Not allowed:

```text
UPDATE
DELETE
```

Corrections must generate new events.

Example:

```text
appointment_created
appointment_corrected
```

---

# Event Indexes

Recommended indexes:

```text
patient_id

event_time

event_type

entity_id

entity_type
```

Compound index:

```text
patient_id + event_time
```

---

# Event Design Principles

1. Immutable
2. Auditable
3. Traceable
4. Explainable
5. Time Ordered
6. Business Meaningful
7. Human Readable

---

# Most Important Collection

```text
events
```

The Patient 360 Timeline, Event Investigation Engine, Root Cause Analysis, Explainability Layer, and Audit Trail all depend on the events collection.

Without events, the platform becomes a standard healthcare application.

With events, it becomes an explainable Patient 360 Agentic AI system.
