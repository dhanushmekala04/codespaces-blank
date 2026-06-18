# AUDIT_LOGGING.md

# Overview

Every important action in the system must be auditable.

Audit logs support:

* Compliance
* Explainability
* Investigations
* Security Monitoring

---

# Audit Collection

audit_logs

---

# Logged Activities

* Login
* Logout
* Appointment Creation
* Appointment Updates
* Claim Access
* Billing Access
* Document Access
* AI Conversations
* Escalations

---

# Agent Audit Record

{
"request_id": "REQ001",
"agent": "BillingAgent",
"prompt_version": "billing_v2",
"model": "GLM-5.1",
"execution_time_ms": 420,
"status": "SUCCESS"
}

---

# API Audit Record

{
"endpoint": "/api/v1/chat",
"user_id": "USR001",
"method": "POST",
"status_code": 200
}

---

# Security Audit Record

{
"event": "UNAUTHORIZED_ACCESS",
"user_id": "USR001",
"timestamp": "2026-06-19T10:00:00Z"
}

---

# Required Fields

* request_id
* user_id
* timestamp
* event_type
* resource
* status

---

# Retention

Standard Logs:

90 Days

Metrics:

1 Year

Audit Logs:

7 Years

---

# Audit Principles

* Immutable
* Searchable
* Timestamped
* Traceable
* Compliant
