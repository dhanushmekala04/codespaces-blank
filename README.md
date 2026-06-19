# PatientCare Platform Architecture

## Overview

PatientCare Platform is a production-grade Patient 360 Healthcare Agentic System built using FastAPI, LangGraph, MongoDB, Redis, and Large Language Models.

The platform automates healthcare workflows including:

* Appointment management
* Billing support
* Insurance assistance
* Prescription refill tracking
* Case monitoring
* Patient timeline analysis
* Healthcare customer support

The system is designed to improve patient experience, reduce administrative workload, and provide explainable healthcare operational intelligence while maintaining safety controls and human escalation pathways.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- MongoDB (local or Atlas)
- Redis (local or cloud)
- OpenAI API Key (or compatible LLM)

### Installation

```bash
# 1. Create virtual environment
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env file (copy from .env and update API keys)
OPENAI_API_KEY=your_key_here
MONGO_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0

# 4. Start MongoDB and Redis (Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest
docker run -d -p 6379:6379 --name redis redis:latest

# 5. Run the application
uvicorn app.main:app --reload --port 8000
```

### Test the API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "patient_id": "PAT001"}'
```

API Documentation: http://localhost:8000/docs

---

# Core Design Principles

* MongoDB is the operational source of truth.
* Every business action generates an event.
* Event history powers Patient 360 timelines.
* Redis improves latency and reduces infrastructure costs.
* Pinecone is used only for knowledge retrieval.
* High-risk healthcare requests are escalated to humans.
* All AI responses are verified before delivery.
* Every decision is auditable and traceable.
* Agents communicate through orchestrated state transitions.
* The platform prioritizes safety, explainability, and compliance.

---

# High-Level Architecture

```text
Patient
    ↓
FastAPI API Layer
    ↓
LangGraph Orchestrator
    ↓
Agent Layer
    ↓
Service Layer
    ↓
Repository Layer
    ↓
MongoDB / Redis / Pinecone
```

---

# Technology Stack

## Backend

* Python 3.12
* FastAPI
* LangGraph
* Pydantic v2
* Motor
* Redis

## AI Layer

* GLM-5.1
* Nemotron-3 Super 120B A12B

## Optional Components

* Pinecone
* Langfuse
* Docker
* OpenTelemetry

---

# LangGraph State

```python
class PatientState(TypedDict):

    patient_id: str

    user_query: str

    intent_result: dict

    planner_result: dict

    appointment_data: dict

    billing_data: dict

    insurance_data: dict

    refill_data: dict

    case_data: dict

    event_analysis: dict

    verification_result: dict

    reflection_result: dict

    final_response: str

    audit_log: list

    escalation_required: bool
```

---

# LangGraph Workflow

```text
START
  │
  ▼
AuthorizationAgent
  │
  ▼
RiskAgent
  │
  ├── ESCALATE
  │
  ▼
IntentAgent
  │
  ▼
PlannerAgent
  │
  ▼
Parallel Specialist Agents
  │
  ├── AppointmentAgent
  ├── BillingAgent
  ├── InsuranceAgent
  ├── RefillAgent
  ├── CaseAgent
  └── EventInvestigationAgent
  │
  ▼
VerificationAgent
  │
  ▼
ReflectionAgent
  │
  ├── Replan
  │
  ▼
ResponseAgent
  │
  ▼
AuditAgent
  │
  ▼
END
```

---

# AI Agents

| Agent                     | Responsibility                  |
| ------------------------- | ------------------------------- |
| Authorization Agent       | Identity and consent validation |
| Risk Agent                | Safety and escalation detection |
| Intent Agent              | Intent and entity extraction    |
| Planner Agent             | Workflow planning               |
| Appointment Agent         | Appointment operations          |
| Billing Agent             | Billing analysis                |
| Insurance Agent           | Insurance and claims            |
| Refill Agent              | Prescription tracking           |
| Case Agent                | Patient case analysis           |
| Event Investigation Agent | Root cause analysis             |
| Verification Agent        | Fact validation                 |
| Reflection Agent          | Completeness review             |
| Response Agent            | Patient-friendly response       |
| Audit Agent               | Compliance logging              |

---

# Event Sourcing

Every business action generates an event.

Collection:

```text
events
```

Example:

```json
{
  "_id": "evt_001",
  "patient_id": "PAT123",
  "event_type": "appointment_rescheduled",
  "event_time": "2026-06-19T10:30:00Z",
  "actor_type": "patient",
  "actor_id": "PAT123",
  "metadata": {
    "old_date": "2026-06-20",
    "new_date": "2026-06-22"
  }
}
```

---

# Patient 360 Timeline

Timeline is generated from event history.

Example:

```text
May 1  Appointment Created
May 3  Lab Ordered
May 6  Lab Completed
May 7  Procedure Completed
May 8  Charge Added
May 10 Claim Submitted
May 12 Claim Approved
May 13 Payment Received
```

---

# Event Investigation Engine

Question:

```text
Why did my bill increase?
```

Timeline:

```text
Procedure Completed
      ↓
Lab Ordered
      ↓
Charge Added
      ↓
Bill Increased
```

Response:

```text
Your balance increased because a laboratory charge
was added after your procedure.
```

---

# MongoDB Collections

## Operational Collections

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
```

## AI Collections

```text
conversation_history
audit_logs
human_review_queue
guardrail_rules
clinician_feedback
```

---

# Example Schemas

## patients

```json
{
  "_id": "PAT123",
  "first_name": "John",
  "last_name": "Doe",
  "dob": "1980-01-01",
  "phone": "",
  "email": "",
  "insurance_id": ""
}
```

## appointments

```json
{
  "_id": "APT001",
  "patient_id": "PAT123",
  "provider_id": "DOC001",
  "status": "scheduled",
  "appointment_date": ""
}
```

## claims

```json
{
  "_id": "CLM001",
  "patient_id": "PAT123",
  "insurance_id": "INS001",
  "status": "denied",
  "denial_reason": "Missing Authorization"
}
```

## billing

```json
{
  "_id": "BILL001",
  "patient_id": "PAT123",
  "balance": 250,
  "charges": []
}
```

---

# Redis Usage

Redis is used for:

* Session cache
* Agent state cache
* Prompt cache
* Context cache
* Response cache
* Rate limiting

Do not cache:

* Billing updates
* Claims
* Payments
* Prescriptions

These should always come from MongoDB.

---

# Pinecone Usage

Pinecone stores knowledge documents only.

Examples:

```text
clinic_policies
insurance_policies
faq
patient_education
provider_guidelines
consent_documents
```

Never store:

* Patients
* Claims
* Appointments
* Billing
* Payments
* Events

Those belong in MongoDB.

---

# Retrieval Flow

```text
Question
    ↓
Embedding
    ↓
Pinecone Search
    ↓
Top Chunks
    ↓
Response Agent
```

---

# Human Escalation

Collection:

```text
human_review_queue
```

Example:

```json
{
  "_id": "HR001",
  "patient_id": "PAT123",
  "reason": "Medication Advice",
  "priority": "HIGH",
  "status": "PENDING"
}
```

Escalation triggers:

* Self-harm
* Emergency symptoms
* Diagnosis requests
* Medication recommendations
* Prescription changes
* Clinical decision support

---

# Tool Layer

Agents should use tools instead of querying databases directly.

```python
get_patient()

get_appointments()

get_claims()

get_billing()

get_refills()

get_case()

get_events()

search_policy_docs()

create_escalation()

write_audit_log()
```

---

# Audit Logging

Every agent execution generates an audit record.

```json
{
  "request_id": "REQ001",
  "agent": "BillingAgent",
  "prompt_version": "billing_v2",
  "execution_time_ms": 420,
  "status": "SUCCESS"
}
```

Collection:

```text
audit_logs
```

---

# API Endpoints

## Chat

```http
POST /api/v1/chat
```

Request:

```json
{
  "patient_id": "PAT123",
  "message": "Why did my bill increase?"
}
```

## Timeline

```http
GET /api/v1/patient/{id}/timeline
```

## Appointments

```http
POST /api/v1/appointments
```

## Claims

```http
GET /api/v1/claims/{claim_id}
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
├── llm/
├── db/
├── middleware/
├── observability/
├── tests/
└── config/
```

---

# Key Differentiator

The platform's primary differentiator is the Patient 360 Event Investigation Engine.

Instead of merely reporting healthcare events, the system explains why they occurred using chronological event evidence, billing records, claim records, appointment history, and policy knowledge.

This enables transparent, auditable, and explainable healthcare operations for patients, providers, and administrators.
