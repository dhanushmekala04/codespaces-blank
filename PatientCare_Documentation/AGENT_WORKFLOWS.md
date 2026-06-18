# AGENT_WORKFLOWS.md

# PatientCare Platform Agent Workflows

## Overview

The PatientCare Platform uses a multi-agent architecture orchestrated through LangGraph.

Each agent has a specific responsibility.

Agents communicate through shared graph state and never communicate directly.

The Planner Agent determines which specialist agents execute for a given request.

---

# Agent Execution Flow

```text
Patient Request
       │
       ▼
Authorization Agent
       │
       ▼
Risk Agent
       │
       ├── Escalate
       │
       ▼
Intent Agent
       │
       ▼
Planner Agent
       │
       ▼
Specialist Agents
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
       │
       ▼
Response Returned
```

---

# Shared State

All agents read and write from the same LangGraph state.

```python
class PatientState(TypedDict):

    request_id: str

    patient_id: str

    user_query: str

    intent_result: dict

    planner_result: dict

    specialist_results: dict

    verification_result: dict

    reflection_result: dict

    final_response: str

    escalation_required: bool

    audit_entries: list
```

---

# Authorization Agent

## Purpose

Validate:

* Patient identity
* Session validity
* Consent status

---

## Input

```text
patient_id
session_id
request
```

---

## Output

```json
{
  "authorized": true,
  "consent_valid": true
}
```

---

## Failure Path

```text
Authorization Failed
         ↓
End Workflow
```

---

# Risk Agent

## Purpose

Identify unsafe requests.

---

## Detect

* Emergency symptoms
* Self-harm
* Medication advice
* Diagnosis requests
* Clinical treatment decisions

---

## Output

```json
{
  "decision": "SAFE",
  "confidence": 0.98
}
```

---

## Escalation Path

```text
Risk Agent
     │
     ├── SAFE
     │
     └── ESCALATE
                │
                ▼
Human Review Queue
```

---

# Intent Agent

## Purpose

Classify user request.

---

## Supported Intents

```text
appointment
billing
insurance
refill
case_status
timeline
event_investigation
general
```

---

## Example

Input:

```text
Why was my claim denied?
```

Output:

```json
{
  "intent": "event_investigation",
  "entities": {
    "claim_id": "CLM001"
  }
}
```

---

# Planner Agent

## Purpose

Determine execution plan.

---

## Example

User Query:

```text
Why was my claim denied?
```

Plan:

```json
{
  "agents": [
    "InsuranceAgent",
    "EventInvestigationAgent"
  ],
  "execution_mode": "parallel"
}
```

---

# Appointment Agent

## Purpose

Handle appointment operations.

---

## Tools

```python
get_appointments()
create_appointment()
update_appointment()
cancel_appointment()
```

---

## Responsibilities

* Appointment history
* Schedule appointment
* Reschedule appointment
* Cancel appointment

---

# Billing Agent

## Purpose

Analyze billing information.

---

## Tools

```python
get_billing()
get_payments()
get_charges()
```

---

## Responsibilities

* Outstanding balance
* Payment history
* Charge explanations

---

# Insurance Agent

## Purpose

Handle insurance information.

---

## Tools

```python
get_claims()
get_insurance()
search_policy_docs()
```

---

## Responsibilities

* Claim status
* Coverage details
* Denial reasons
* Policy lookup

---

# Refill Agent

## Purpose

Manage prescription refill workflows.

---

## Tools

```python
get_prescriptions()
get_refills()
create_refill_request()
```

---

## Responsibilities

* Refill tracking
* Refill requests
* Refill status

---

# Case Agent

## Purpose

Build Patient 360 understanding.

---

## Tools

```python
get_case()
get_events()
get_appointments()
get_claims()
```

---

## Responsibilities

* Case summary
* Active items
* Open tasks
* Patient timeline summary

---

## Example Output

```json
{
  "case_summary": "Patient has one active claim and an upcoming appointment.",
  "active_items": [
    "Claim Review",
    "Upcoming Appointment"
  ]
}
```

---

# Event Investigation Agent

## Purpose

Determine why events occurred.

---

## Tools

```python
get_events()
get_claims()
get_billing()
get_payments()
```

---

## Investigation Process

Step 1

Build timeline.

Step 2

Locate target event.

Step 3

Find preceding events.

Step 4

Determine causal relationships.

Step 5

Generate root cause.

---

## Example

Timeline:

```text
Procedure Completed
      ↓
Charge Added
      ↓
Bill Increased
```

Output:

```json
{
  "root_cause": "Laboratory charge added after procedure.",
  "confidence": 0.95
}
```

---

# Parallel Execution

Example:

```text
Question:
Why did my bill increase and was my claim approved?
```

Planner:

```json
{
  "agents": [
    "BillingAgent",
    "InsuranceAgent",
    "EventInvestigationAgent"
  ]
}
```

Execution:

```text
Billing Agent
        │
Insurance Agent
        │
Event Agent
        │
        ▼
Merge Results
```

---

# Verification Agent

## Purpose

Fact validation.

---

## Checks

* Unsupported claims
* Missing evidence
* Hallucinations
* Contradictions

---

## Output

```json
{
  "status": "PASS",
  "issues": []
}
```

---

# Reflection Agent

## Purpose

Completeness review.

---

## Questions

* Was every intent answered?
* Is additional data needed?
* Is replanning required?

---

## Output

```json
{
  "complete": true,
  "replan_required": false
}
```

---

# Response Agent

## Purpose

Generate patient-friendly responses.

---

## Rules

* Simple language
* Professional tone
* No diagnosis
* No medication recommendations

---

## Example

Instead of:

```text
Authorization deficiency resulted in claim adjudication failure.
```

Generate:

```text
Your claim was denied because prior authorization was not completed before the procedure.
```

---

# Audit Agent

## Purpose

Record workflow execution.

---

## Logged Information

```json
{
  "request_id": "REQ001",
  "agent": "BillingAgent",
  "execution_time_ms": 432,
  "status": "SUCCESS",
  "prompt_version": "billing_v2"
}
```

---

# Human Escalation Workflow

```text
Risk Agent
      │
      ▼
Escalation Queue
      │
      ▼
Human Reviewer
      │
      ▼
Patient Response
```

---

# Workflow Examples

## Appointment Query

```text
Patient:
When is my next appointment?

Workflow:

Authorization
      ↓
Risk
      ↓
Intent
      ↓
Planner
      ↓
Appointment Agent
      ↓
Verification
      ↓
Response
```

---

## Claim Denial Investigation

```text
Patient:
Why was my claim denied?

Workflow:

Authorization
      ↓
Risk
      ↓
Intent
      ↓
Planner
      ↓
Insurance Agent
      ↓
Event Investigation Agent
      ↓
Verification
      ↓
Response
```

---

# Summary

The workflow architecture is designed around:

* Safety first
* Explainability
* Event-driven reasoning
* Parallel agent execution
* Human escalation
* Auditable decisions

The Event Investigation Agent, Case Agent, and Planner Agent form the intelligence core of the PatientCare Platform.
