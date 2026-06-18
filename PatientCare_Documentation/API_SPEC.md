# API_SPEC.md

# PatientCare Platform API Specification

## Overview

This document defines the REST API contracts for the PatientCare Platform.

Base URL:

```text
/api/v1
```

API Principles:

* RESTful Design
* JSON Request/Response
* Stateless APIs
* JWT Authentication
* Audit Logging
* Role-Based Access Control
* Versioned Endpoints

---

# Authentication

## Login

### Endpoint

```http
POST /api/v1/auth/login
```

### Request

```json
{
  "email": "patient@example.com",
  "password": "********"
}
```

### Response

```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## Refresh Token

### Endpoint

```http
POST /api/v1/auth/refresh
```

### Response

```json
{
  "access_token": "new_token"
}
```

---

# Patient APIs

## Get Patient Profile

### Endpoint

```http
GET /api/v1/patients/{patient_id}
```

### Response

```json
{
  "patient_id": "PAT001",
  "first_name": "John",
  "last_name": "Doe",
  "insurance_id": "INS001"
}
```

---

## Update Patient Profile

### Endpoint

```http
PUT /api/v1/patients/{patient_id}
```

### Request

```json
{
  "phone": "+1-555-1234",
  "email": "john@example.com"
}
```

---

# AI Chat Endpoint

## Chat with PatientCare Agent

### Endpoint

```http
POST /api/v1/chat
```

### Purpose

Entry point into LangGraph workflow.

---

### Request

```json
{
  "patient_id": "PAT001",
  "message": "Why was my claim denied?"
}
```

---

### Response

```json
{
  "request_id": "REQ001",
  "response": "Your claim was denied because prior authorization was missing.",
  "sources": [
    "claim_record",
    "event_timeline"
  ]
}
```

---

# Timeline APIs

## Get Patient Timeline

### Endpoint

```http
GET /api/v1/patients/{patient_id}/timeline
```

### Query Parameters

```text
start_date
end_date
limit
offset
```

---

### Response

```json
{
  "events": [
    {
      "event_type": "appointment_created",
      "event_time": "2026-06-01T10:00:00Z"
    }
  ]
}
```

---

## Get Timeline Event

### Endpoint

```http
GET /api/v1/events/{event_id}
```

---

### Response

```json
{
  "event_id": "EVT001",
  "event_type": "claim_denied",
  "metadata": {}
}
```

---

# Appointment APIs

## Create Appointment

### Endpoint

```http
POST /api/v1/appointments
```

### Request

```json
{
  "patient_id": "PAT001",
  "provider_id": "PROV001",
  "appointment_date": "2026-07-01"
}
```

---

### Response

```json
{
  "appointment_id": "APT001",
  "status": "scheduled"
}
```

---

## Get Appointments

### Endpoint

```http
GET /api/v1/appointments
```

### Query Parameters

```text
patient_id
status
limit
offset
```

---

## Reschedule Appointment

### Endpoint

```http
PUT /api/v1/appointments/{appointment_id}/reschedule
```

### Request

```json
{
  "new_date": "2026-07-05"
}
```

---

## Cancel Appointment

### Endpoint

```http
DELETE /api/v1/appointments/{appointment_id}
```

---

# Billing APIs

## Get Billing Summary

### Endpoint

```http
GET /api/v1/billing/{patient_id}
```

### Response

```json
{
  "balance": 250,
  "charges": [],
  "payments": []
}
```

---

## Get Payment History

### Endpoint

```http
GET /api/v1/payments/{patient_id}
```

---

### Response

```json
{
  "payments": [
    {
      "payment_id": "PAY001",
      "amount": 100
    }
  ]
}
```

---

# Insurance APIs

## Get Insurance Information

### Endpoint

```http
GET /api/v1/insurance/{patient_id}
```

### Response

```json
{
  "insurance_id": "INS001",
  "provider_name": "ABC Insurance",
  "plan_name": "Premium Gold"
}
```

---

## Get Claim Details

### Endpoint

```http
GET /api/v1/claims/{claim_id}
```

### Response

```json
{
  "claim_id": "CLM001",
  "status": "denied",
  "denial_reason": "Missing Authorization"
}
```

---

## Get Patient Claims

### Endpoint

```http
GET /api/v1/claims
```

### Query Parameters

```text
patient_id
status
limit
offset
```

---

# Refill APIs

## Create Refill Request

### Endpoint

```http
POST /api/v1/refills
```

### Request

```json
{
  "prescription_id": "RX001"
}
```

---

### Response

```json
{
  "refill_id": "REF001",
  "status": "requested"
}
```

---

## Get Refill Status

### Endpoint

```http
GET /api/v1/refills/{refill_id}
```

---

### Response

```json
{
  "refill_id": "REF001",
  "status": "pending"
}
```

---

# Clinical Documents APIs

## Upload Document

### Endpoint

```http
POST /api/v1/documents
```

### Content Type

```text
multipart/form-data
```

---

### Response

```json
{
  "document_id": "DOC001",
  "status": "uploaded"
}
```

---

## Get Document Metadata

### Endpoint

```http
GET /api/v1/documents/{document_id}
```

---

# Case APIs

## Get Case Summary

### Endpoint

```http
GET /api/v1/cases/{case_id}
```

### Response

```json
{
  "case_id": "CASE001",
  "status": "open",
  "priority": "medium"
}
```

---

## Get Patient Cases

### Endpoint

```http
GET /api/v1/cases
```

---

# Event Investigation APIs

## Investigate Event

### Endpoint

```http
POST /api/v1/events/investigate
```

### Request

```json
{
  "patient_id": "PAT001",
  "question": "Why did my bill increase?"
}
```

---

### Response

```json
{
  "root_cause": "A laboratory charge was added after the appointment.",
  "confidence": 0.96,
  "evidence": [
    "Lab Ordered",
    "Charge Added"
  ]
}
```

---

# Human Escalation APIs

## Get Escalated Cases

### Endpoint

```http
GET /api/v1/escalations
```

---

### Response

```json
{
  "items": []
}
```

---

## Create Escalation

### Endpoint

```http
POST /api/v1/escalations
```

### Request

```json
{
  "patient_id": "PAT001",
  "reason": "Medication Advice"
}
```

---

# Admin APIs

## Get Audit Logs

### Endpoint

```http
GET /api/v1/admin/audit-logs
```

---

## Get Agent Metrics

### Endpoint

```http
GET /api/v1/admin/metrics
```

---

### Response

```json
{
  "requests_processed": 10000,
  "average_response_time_ms": 750,
  "escalation_rate": 0.04
}
```

---

# Pagination Standard

## Request

```text
?page=1
&page_size=20
```

---

## Response

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total_records": 100,
  "total_pages": 5
}
```

---

# Standard Success Response

```json
{
  "success": true,
  "data": {}
}
```

---

# Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Patient not found"
  }
}
```

---

# Common HTTP Status Codes

```text
200 OK

201 Created

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

429 Too Many Requests

500 Internal Server Error
```

---

# Security Requirements

All endpoints must support:

* JWT Authentication
* HTTPS
* Role-Based Access Control
* Audit Logging
* Rate Limiting

---

# API Versioning

Current Version:

```text
v1
```

Future Versions:

```text
v2
v3
```

Versioning Strategy:

```http
/api/v1/...
```

---

# API Design Goals

* Consistency
* Security
* Scalability
* Auditability
* Explainability
* Healthcare Compliance

These APIs form the communication layer between the frontend, LangGraph agents, MongoDB, Redis, Pinecone, and administrative systems.
