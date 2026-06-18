# PatientCare Platform

> Production-Grade Patient 360 Healthcare Agentic AI System built with FastAPI, LangGraph, MongoDB, Redis, and Large Language Models.

---

# Overview

PatientCare Platform is an intelligent Healthcare Patient 360 system that automates operational healthcare workflows while providing explainable patient support through a multi-agent AI architecture.

The platform enables healthcare organizations to:

* Manage appointments
* Track insurance claims
* Monitor billing activities
* Handle prescription refills
* Analyze patient cases
* Generate Patient 360 timelines
* Explain healthcare events
* Escalate high-risk situations safely

Unlike traditional healthcare chatbots, PatientCare Platform focuses on **event-driven patient intelligence**, allowing patients and healthcare staff to understand not only what happened, but also why it happened.

---

# Key Features

## Patient Services

* Appointment scheduling
* Appointment rescheduling
* Appointment cancellation
* Appointment history retrieval
* Billing support
* Payment tracking
* Insurance claim tracking
* Insurance coverage assistance
* Prescription refill tracking
* Case monitoring
* Clinical document retrieval

---

## Patient 360 Timeline

The platform maintains a complete event-driven timeline for every patient.

Example timeline:

```text
Appointment Created
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
Claim Approved
       ↓
Payment Received
```

Patients can ask:

* Why did my bill increase?
* Why was my claim denied?
* What happened in my case?
* Which procedure generated this charge?
* Who changed my appointment?

---

## Event Investigation Engine

One of the most powerful capabilities of the platform is the Event Investigation Engine.

Example:

Patient asks:

```text
Why was my claim denied?
```

System response:

```text
Your claim was denied because prior authorization
was not completed before the MRI procedure.

Evidence:
- MRI Procedure Ordered
- Prior Authorization Missing
- Claim Submitted
- Claim Denied
```

The platform uses event chronology and operational records to generate explainable responses.

---

# Architecture

```text
Patient
    │
    ▼
FastAPI API Layer
    │
    ▼
LangGraph Orchestrator
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

# Technology Stack

## Backend

* Python 3.12
* FastAPI
* Pydantic v2
* Motor
* AsyncIO

## Agent Framework

* LangGraph
* LangChain

## Databases

* MongoDB
* Redis

## Knowledge Retrieval

* Pinecone
* Embedding Models

## LLM Models

### GLM-5.1

Used for:

* Intent Classification
* Workflow Planning
* Insurance Support
* Billing Support
* Refill Support
* Verification
* Response Generation

### Nemotron-3 Super 120B A12B

Used for:

* Patient Timeline Analysis
* Event Correlation
* Root Cause Investigation
* Long Context Case Analysis

---

# Multi-Agent Architecture

| Agent                     | Responsibility         |
| ------------------------- | ---------------------- |
| Authorization Agent       | Identity verification  |
| Risk Agent                | Safety assessment      |
| Intent Agent              | Intent classification  |
| Planner Agent             | Workflow planning      |
| Appointment Agent         | Appointment operations |
| Billing Agent             | Billing analysis       |
| Insurance Agent           | Insurance support      |
| Refill Agent              | Prescription tracking  |
| Case Agent                | Patient case analysis  |
| Event Investigation Agent | Root cause analysis    |
| Verification Agent        | Fact validation        |
| Reflection Agent          | Completeness review    |
| Response Agent            | Patient communication  |
| Audit Agent               | Compliance logging     |

---

# Workflow

```text
Authorization Agent
        │
        ▼
Risk Agent
        │
        ▼
Intent Agent
        │
        ▼
Planner Agent
        │
        ▼
Parallel Specialist Agents
        │
        ├── Appointment Agent
        ├── Billing Agent
        ├── Insurance Agent
        ├── Refill Agent
        ├── Case Agent
        └── Event Investigation Agent
        │
        ▼
Verification Agent
        │
        ▼
Reflection Agent
        │
        ▼
Response Agent
        │
        ▼
Audit Agent
```

---

# Data Architecture

## MongoDB

MongoDB acts as the operational source of truth.

### Collections

```text
patients
providers
appointments
cases
claims
insurance
billing
payments
prescriptions
refills
lab_results
procedures
clinical_documents
events
```

### AI Collections

```text
conversation_history
audit_logs
human_review_queue
guardrail_rules
clinician_feedback
```

---

## Redis

Used for:

* Session caching
* Agent state caching
* Prompt caching
* Context caching
* Response caching
* Rate limiting

---

## Pinecone

Pinecone stores healthcare knowledge documents only.

Examples:

```text
clinic_policies
insurance_policies
faq
patient_education
provider_guidelines
consent_documents
```

Operational healthcare data is never stored in Pinecone.

---

# Event Sourcing

Every business action generates an event.

Example:

```json
{
  "_id": "evt_001",
  "patient_id": "PAT123",
  "event_type": "claim_denied",
  "event_time": "2026-06-19T10:30:00Z",
  "metadata": {
    "reason": "Missing Authorization"
  }
}
```

These events power:

* Timeline generation
* Root cause analysis
* Billing explanations
* Claim investigations
* Audit trails

---

# Safety & Human Escalation

The platform never provides:

* Diagnoses
* Medication recommendations
* Clinical treatment decisions

The following situations are automatically escalated:

* Self-harm concerns
* Emergency symptoms
* Medication advice requests
* Prescription modifications
* Clinical decision requests

Escalations are stored in:

```text
human_review_queue
```

---

# API Endpoints

## Chat

```http
POST /api/v1/chat
```

## Timeline

```http
GET /api/v1/patient/{patient_id}/timeline
```

## Claims

```http
GET /api/v1/claims/{claim_id}
```

## Appointments

```http
POST /api/v1/appointments
```

---

# Project Structure

```text
app/
│
├── api/
├── agents/
├── graph/
├── services/
├── repositories/
├── schemas/
├── db/
├── llm/
├── middleware/
├── observability/
├── tests/
└── config/
```

---

# Core Design Principles

* MongoDB is the operational source of truth.
* Every business action creates an event.
* Event history powers Patient 360 timelines.
* Redis improves performance and reduces cost.
* Pinecone is used only for semantic retrieval.
* All AI outputs are verified before delivery.
* Every decision is auditable and traceable.
* Human escalation is prioritized over unsafe automation.
* Safety and explainability come before autonomy.

---

# Future Roadmap

## Phase 1

* Patient Authentication
* Appointment Management
* Billing Support
* Insurance Tracking
* Event Logging

## Phase 2

* Multi-Agent Orchestration
* Patient Timeline Engine
* Root Cause Investigation

## Phase 3

* Pinecone Knowledge Base
* Policy Retrieval
* FAQ Search
* Patient Education Retrieval

## Phase 4

* Langfuse Observability
* OpenTelemetry
* Prometheus
* Grafana
* Production Monitoring

---

# Why This Project Matters

Most healthcare chatbots only answer questions.

PatientCare Platform goes further by:

* Understanding healthcare workflows
* Maintaining patient timelines
* Investigating healthcare events
* Explaining operational decisions
* Providing transparent and auditable reasoning

The result is a Patient 360 system that improves both patient experience and healthcare operational efficiency.

---

# License

MIT License

---

# Author

Dhanush Vardhan

AI / ML Engineer

Specializing in:

* Agentic AI
* LangGraph
* Healthcare AI
* RAG Systems
* Multi-Agent Orchestration
* Production LLM Applications
