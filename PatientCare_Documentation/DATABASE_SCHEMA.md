# DATABASE_SCHEMA.md

# PatientCare Platform Database Schema

## Overview

MongoDB is the operational source of truth for the PatientCare Platform.

The database is divided into:

1. Operational Collections
2. AI Collections
3. Audit Collections
4. Event Collections

---

# Database Principles

* MongoDB stores all operational healthcare data.
* Every business action generates an event.
* Events are immutable.
* Patient timelines are generated from events.
* AI agents never modify records directly.
* Service layer performs all database writes.

---

# Collection Relationships

```text
Patient
 │
 ├── Appointments
 ├── Cases
 ├── Claims
 ├── Billing
 ├── Payments
 ├── Prescriptions
 ├── Refills
 ├── Clinical Documents
 └── Events
```

---

# patients

Stores patient demographic information.

## Schema

```json
{
  "_id": "PAT001",

  "first_name": "John",

  "last_name": "Doe",

  "date_of_birth": "1980-01-01",

  "gender": "Male",

  "phone": "+1-555-1111",

  "email": "john@example.com",

  "insurance_id": "INS001",

  "created_at": "2026-01-01T10:00:00Z",

  "updated_at": "2026-01-01T10:00:00Z"
}
```

## Indexes

```text
patient_id
email
phone
insurance_id
```

---

# providers

Stores provider information.

## Schema

```json
{
  "_id": "PROV001",

  "provider_name": "Dr Smith",

  "specialty_id": "SPEC001",

  "status": "active"
}
```

---

# specialties

```json
{
  "_id": "SPEC001",

  "name": "Cardiology"
}
```

---

# appointments

Stores patient appointments.

## Schema

```json
{
  "_id": "APT001",

  "patient_id": "PAT001",

  "provider_id": "PROV001",

  "appointment_date": "2026-06-20",

  "status": "scheduled",

  "created_at": "2026-06-01T10:00:00Z"
}
```

## Status Values

```text
scheduled
confirmed
completed
cancelled
rescheduled
no_show
```

---

# cases

Represents healthcare cases.

## Schema

```json
{
  "_id": "CASE001",

  "patient_id": "PAT001",

  "status": "open",

  "priority": "medium",

  "opened_date": "2026-06-01",

  "closed_date": null
}
```

---

# procedures

Stores performed procedures.

## Schema

```json
{
  "_id": "PROC001",

  "patient_id": "PAT001",

  "case_id": "CASE001",

  "procedure_name": "MRI",

  "procedure_date": "2026-06-10"
}
```

---

# lab_results

Stores laboratory information.

## Schema

```json
{
  "_id": "LAB001",

  "patient_id": "PAT001",

  "case_id": "CASE001",

  "lab_name": "CBC",

  "status": "completed",

  "completed_at": "2026-06-12"
}
```

---

# insurance

Stores patient insurance information.

## Schema

```json
{
  "_id": "INS001",

  "patient_id": "PAT001",

  "provider_name": "ABC Insurance",

  "plan_name": "Premium Gold",

  "status": "active"
}
```

---

# claims

Stores insurance claims.

## Schema

```json
{
  "_id": "CLM001",

  "patient_id": "PAT001",

  "insurance_id": "INS001",

  "claim_amount": 500,

  "status": "denied",

  "denial_reason": "Missing Authorization",

  "submitted_at": "2026-06-01"
}
```

## Status Values

```text
draft
submitted
processing
approved
denied
paid
```

---

# billing

Stores patient billing information.

## Schema

```json
{
  "_id": "BILL001",

  "patient_id": "PAT001",

  "total_balance": 250,

  "charges": [
    {
      "charge_id": "CH001",
      "description": "MRI",
      "amount": 250
    }
  ]
}
```

---

# payments

Stores payment history.

## Schema

```json
{
  "_id": "PAY001",

  "patient_id": "PAT001",

  "bill_id": "BILL001",

  "amount": 100,

  "payment_date": "2026-06-15"
}
```

---

# prescriptions

Stores prescription records.

## Schema

```json
{
  "_id": "RX001",

  "patient_id": "PAT001",

  "prescription_name": "Medication A",

  "status": "active"
}
```

---

# refills

Stores refill requests.

## Schema

```json
{
  "_id": "REF001",

  "patient_id": "PAT001",

  "prescription_id": "RX001",

  "status": "requested"
}
```

---

# clinical_documents

Stores metadata for uploaded healthcare documents.

## Schema

```json
{
  "_id": "DOC001",

  "patient_id": "PAT001",

  "document_type": "Lab Report",

  "storage_path": "/documents/doc001.pdf",

  "uploaded_at": "2026-06-01"
}
```

---

# events

Most important collection.

Used for:

* Patient 360 Timeline
* Root Cause Analysis
* Event Investigation
* Audit Trails

## Schema

```json
{
  "_id": "EVT001",

  "patient_id": "PAT001",

  "event_type": "claim_denied",

  "event_time": "2026-06-15T10:00:00Z",

  "actor_type": "system",

  "actor_id": "SYSTEM",

  "metadata": {
    "claim_id": "CLM001",
    "reason": "Missing Authorization"
  }
}
```

## Event Types

```text
appointment_created

appointment_rescheduled

appointment_cancelled

appointment_completed

lab_ordered

lab_completed

procedure_completed

claim_submitted

claim_approved

claim_denied

charge_added

payment_received

prescription_created

refill_requested

refill_approved

case_opened

case_closed
```

---

# conversation_history

Stores patient-agent conversations.

## Schema

```json
{
  "_id": "CHAT001",

  "patient_id": "PAT001",

  "message": "Why was my claim denied?",

  "response": "...",

  "created_at": "2026-06-15T10:00:00Z"
}
```

---

# audit_logs

Stores agent execution history.

## Schema

```json
{
  "_id": "AUD001",

  "request_id": "REQ001",

  "agent": "BillingAgent",

  "prompt_version": "billing_v2",

  "execution_time_ms": 420,

  "status": "SUCCESS"
}
```

---

# human_review_queue

Stores escalated requests.

## Schema

```json
{
  "_id": "HR001",

  "patient_id": "PAT001",

  "reason": "Medication Advice",

  "priority": "HIGH",

  "status": "PENDING"
}
```

---

# guardrail_rules

Stores configurable AI safety rules.

## Schema

```json
{
  "_id": "RULE001",

  "rule_name": "Medication Advice",

  "action": "ESCALATE"
}
```

---

# Database Summary

## Core Collections

```text
patients
appointments
cases
claims
billing
payments
insurance
prescriptions
refills
clinical_documents
events
```

## AI Collections

```text
conversation_history
audit_logs
human_review_queue
guardrail_rules
clinician_feedback
```

## Most Critical Collection

```text
events
```

The Patient 360 Timeline, Event Investigation Engine, Root Cause Analysis, and Explainability layer are all powered by the events collection.
