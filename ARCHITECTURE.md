# Healthcare Patient 360 Agentic Platform

## Overview

The Healthcare Patient 360 Agentic Platform is a multi-agent AI system designed to automate healthcare operational workflows while maintaining safety, compliance, and human oversight. The platform assists patients with appointment management, billing inquiries, insurance questions, prescription refill tracking, case status monitoring, timeline explanations, and patient support operations. The system does not provide diagnoses, medication recommendations, or clinical decision-making. Any medical or high-risk request is automatically escalated to a human clinician or staff member.

---

# Architecture Overview

```text
Patient
    │
    ▼
FastAPI API Layer
    │
    ▼
LangGraph Agent Orchestrator
    │
    ▼
Agent Layer
    │
    ▼
Service Layer
    │
    ▼
Repository Layer
    │
    ▼
MongoDB / Redis / Pinecone
```

---

# Data Architecture

## MongoDB (Primary System of Record)

MongoDB stores all operational healthcare data and acts as the authoritative source of truth.

### Collections

```text
patients
providers
specialties
cases
appointments
lab_results
procedures
prescriptions
refills
insurance
claims
billing
payments
clinical_documents
events

conversation_history
audit_logs
human_review_queue
guardrail_rules
clinician_feedback
```

Every business action generates an event which is stored in the events collection to enable Patient 360 timeline reconstruction and root-cause analysis.

---

## Redis (Performance Layer)

Redis is used for:

```text
Session Cache
Agent State Cache
Response Cache
Prompt Cache
Rate Limiting
Conversation Summaries
Context Caching
```

Redis improves response times and reduces LLM and database costs.

---

## Pinecone (Knowledge Layer - Optional)

Pinecone is used only for semantic search and Retrieval-Augmented Generation (RAG).

### Stored Content

```text
Clinic Policies
Insurance Guidelines
FAQ Documents
Provider Documentation
Consent Forms
Patient Education Material
Operational Procedures
```

### Not Stored

```text
Patients
Appointments
Claims
Billing
Payments
Cases
Refills
Events
```

Operational records always remain in MongoDB.

---

# Patient 360 Design

Every patient has a unified view across:

```text
Appointments
Cases
Lab Results
Procedures
Prescriptions
Insurance
Claims
Billing
Payments
Documents
Events
```

The Patient 360 Timeline allows the system to answer questions such as:

```text
Why did my bill increase?

Why was my claim denied?

Who changed my appointment?

What happened in my case?

Which procedure generated this charge?
```

---

# Event-Driven Architecture

Every business operation generates an event.

### Appointment Events

```text
appointment_created
appointment_rescheduled
appointment_cancelled
appointment_completed
```

### Billing Events

```text
bill_created
charge_added
payment_received
refund_processed
```

### Insurance Events

```text
claim_submitted
claim_approved
claim_denied
coverage_verified
```

### Prescription Events

```text
refill_requested
refill_ready
refill_completed
```

### Case Events

```text
case_opened
procedure_ordered
lab_ordered
lab_completed
case_closed
```

---

# Agent-to-Model Mapping

| Agent                     | Model                      |
| ------------------------- | -------------------------- |
| Authorization Agent       | Rule Engine                |
| Risk Agent                | GLM-5.1                    |
| Intent Agent              | GLM-5.1                    |
| Planner Agent             | GLM-5.1                    |
| Appointment Agent         | GLM-5.1                    |
| Billing Agent             | GLM-5.1                    |
| Insurance Agent           | GLM-5.1                    |
| Refill Agent              | GLM-5.1                    |
| Case Agent                | Nemotron-3 Super 120B A12B |
| Event Investigation Agent | Nemotron-3 Super 120B A12B |
| Verification Agent        | GLM-5.1                    |
| Reflection Agent          | GLM-5.1                    |
| Response Agent            | GLM-5.1                    |
| Audit Agent               | Rule Engine                |

---

# Agent Responsibilities

## Authorization Agent

Validates authentication, patient identity, tenant isolation, and consent permissions.

## Risk Agent

Detects emergencies, medical advice requests, diagnosis requests, self-harm indicators, and high-risk content.

## Intent Agent

Identifies patient intent and extracts relevant entities such as dates, appointment IDs, claim IDs, and case IDs.

## Planner Agent

Creates execution plans and selects specialist agents required to fulfill the request.

## Appointment Agent

Handles appointment scheduling, rescheduling, cancellation, availability lookup, and appointment history.

## Billing Agent

Provides balance information, billing history, charge explanations, and payment tracking.

## Insurance Agent

Handles coverage lookup, eligibility checks, claim status, and claim history.

## Refill Agent

Tracks prescriptions, refill requests, and medication refill status.

## Case Agent

Provides Patient 360 case summaries including appointments, procedures, lab results, and documents.

## Event Investigation Agent

Performs timeline analysis and root-cause investigation to determine why an event occurred.

## Verification Agent

Validates facts, checks consistency, and prevents hallucinated responses.

## Reflection Agent

Reviews response completeness and determines whether additional processing is required.

## Response Agent

Generates patient-friendly responses using verified information.

## Audit Agent

Records all decisions, tool calls, execution traces, costs, and compliance logs.

---

# Workflow

```text
Authorization
      ↓
Risk
      ↓
Intent
      ↓
Planner
      ↓
Specialist Agents
      ↓
Event Investigation
      ↓
Verification
      ↓
Reflection
      ↓
Response
      ↓
Audit
```

Escalation Flow:

```text
Authorization
      ↓
Risk
      ↓
Human Review Queue
      ↓
Audit
```

---

# Core Design Principles

* MongoDB is the operational source of truth.
* Every business action generates an event.
* Event history powers Patient 360 timelines.
* Redis reduces latency and infrastructure costs.
* Pinecone is used only for knowledge retrieval.
* High-risk healthcare requests are escalated.
* All AI responses are validated before delivery.
* Every action is auditable and traceable.
* Agents communicate through shared state and orchestration.
* The system prioritizes safety, explainability, and compliance.
