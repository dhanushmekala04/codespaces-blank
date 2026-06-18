# HUMAN_ESCALATION.md

# PatientCare Platform Human Escalation Framework

## Overview

The PatientCare Platform is designed to automate operational healthcare workflows while ensuring patient safety.

Certain requests must never be handled exclusively by AI.

These requests are escalated to qualified human reviewers.

---

# Core Principle

```text
Safe → AI Response

Unsafe → Human Review
```

Patient safety always takes priority over automation.

---

# Escalation Architecture

```text
Patient Request
       │
       ▼
Risk Agent
       │
 ┌─────┴─────┐
 ▼           ▼
SAFE     ESCALATE
 │           │
 ▼           ▼
AI       Human Queue
 │           │
 ▼           ▼
Response  Human Review
```

---

# Escalation Triggers

## Emergency Symptoms

Examples:

* Chest pain
* Difficulty breathing
* Severe bleeding
* Stroke symptoms
* Loss of consciousness

Action:

```text
Immediate Escalation
```

Priority:

```text
CRITICAL
```

---

## Self-Harm

Examples:

* Suicide ideation
* Self-harm intent
* Harm to others

Action:

```text
Immediate Escalation
```

Priority:

```text
CRITICAL
```

---

## Diagnosis Requests

Examples:

* What disease do I have?
* Diagnose my symptoms

Action:

```text
Escalate
```

Priority:

```text
HIGH
```

---

## Medication Advice

Examples:

* Should I take this medicine?
* Increase dosage?
* Change medication?

Action:

```text
Escalate
```

Priority:

```text
HIGH
```

---

## Treatment Decisions

Examples:

* Should I have surgery?
* Which treatment is better?

Action:

```text
Escalate
```

Priority:

```text
HIGH
```

---

## Legal / Compliance Requests

Examples:

* Insurance disputes
* Legal complaints
* Regulatory concerns

Priority:

```text
MEDIUM
```

---

# Escalation Queue

Collection:

```text
human_review_queue
```

---

# Queue Schema

```json
{
  "_id": "HR001",

  "patient_id": "PAT001",

  "request_id": "REQ001",

  "reason": "Medication Advice",

  "priority": "HIGH",

  "status": "PENDING",

  "created_at": "2026-06-19T10:00:00Z"
}
```

---

# Priority Levels

## CRITICAL

Target Response:

```text
< 5 Minutes
```

Examples:

* Self-harm
* Emergency symptoms

---

## HIGH

Target Response:

```text
< 30 Minutes
```

Examples:

* Medication advice
* Diagnosis requests

---

## MEDIUM

Target Response:

```text
< 4 Hours
```

Examples:

* Billing disputes
* Insurance disputes

---

## LOW

Target Response:

```text
< 24 Hours
```

Examples:

* Documentation review
* Administrative requests

---

# Human Reviewer Roles

## Clinical Reviewer

Handles:

* Clinical questions
* Diagnosis requests
* Treatment questions

---

## Billing Reviewer

Handles:

* Billing disputes
* Charge investigations

---

## Insurance Reviewer

Handles:

* Coverage questions
* Appeals
* Denials

---

## Compliance Reviewer

Handles:

* Legal requests
* Privacy concerns
* Security incidents

---

# Escalation Workflow

```text
Patient Request
       │
       ▼
Risk Agent
       │
       ▼
Escalation Queue
       │
       ▼
Human Reviewer
       │
       ▼
Resolution
       │
       ▼
Patient Response
```

---

# Escalation Audit Log

```json
{
  "request_id": "REQ001",

  "escalation_reason": "Medication Advice",

  "priority": "HIGH",

  "reviewer": "USR001",

  "resolved_at": "2026-06-19T10:20:00Z"
}
```

---

# Human-in-the-Loop Design

The AI system:

* Identifies risk
* Collects evidence
* Summarizes context

The human:

* Makes decisions
* Provides recommendations
* Approves responses

---

# Escalation Metrics

Track:

* Escalations Per Day
* Resolution Time
* Escalation Reason Distribution
* Reviewer Workload
* Escalation Accuracy

---

# Goals

* Patient Safety
* Regulatory Compliance
* Human Oversight
* Responsible AI Deployment

No clinical decision should be made without qualified human review.
