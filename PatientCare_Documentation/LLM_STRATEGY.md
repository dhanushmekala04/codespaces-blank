# LLM_STRATEGY.md

# PatientCare Platform LLM Strategy

## Overview

The PatientCare Platform uses a multi-model architecture.

Different agents use different Large Language Models based on:

* Cost
* Latency
* Context Length
* Reasoning Complexity
* Reliability
* Structured Output Requirements

The goal is to use the smallest model capable of completing the task safely and accurately.

---

# Design Principles

1. Cost Optimization
2. Low Latency
3. Explainability
4. Structured Outputs
5. Safety First
6. Model Specialization
7. Verification Before Response

---

# Model Architecture

```text
Patient Request
        │
        ▼
LangGraph
        │
        ▼
Agent Routing
        │
 ┌──────┴──────┐
 ▼             ▼
GLM-5.1    Nemotron 120B
 │             │
 └──────┬──────┘
        ▼
Verification
        ▼
Reflection
        ▼
Response
```

---

# Primary Models

## GLM-5.1

Default model for most platform operations.

### Responsibilities

* Intent Classification
* Entity Extraction
* Workflow Planning
* Appointment Support
* Billing Support
* Insurance Support
* Refill Support
* Verification
* Reflection
* Response Generation

### Why GLM-5.1?

Benefits:

```text
Fast

Lower Cost

Strong Tool Calling

Structured Outputs

Reliable Classification
```

### Example Tasks

Question:

```text
What is my claim status?
```

Question:

```text
When is my next appointment?
```

Question:

```text
How much do I owe?
```

These should use GLM-5.1.

---

# Nemotron-3 Super 120B A12B

Large reasoning model.

Used only for complex analysis.

### Responsibilities

* Case Analysis
* Patient 360 Summaries
* Event Investigation
* Timeline Correlation
* Root Cause Analysis
* Long Context Reasoning

### Why Nemotron?

Benefits:

```text
Deep Reasoning

Long Context

Chronological Analysis

Complex Multi-Step Thinking
```

### Example Tasks

Question:

```text
Why did my bill increase?
```

Question:

```text
What happened in my case over the last six months?
```

Question:

```text
Why was my claim denied?
```

These should use Nemotron.

---

# Agent to Model Mapping

| Agent                   | Model    |
| ----------------------- | -------- |
| AuthorizationAgent      | GLM-5.1  |
| RiskAgent               | GLM-5.1  |
| IntentAgent             | GLM-5.1  |
| PlannerAgent            | GLM-5.1  |
| AppointmentAgent        | GLM-5.1  |
| BillingAgent            | GLM-5.1  |
| InsuranceAgent          | GLM-5.1  |
| RefillAgent             | GLM-5.1  |
| VerificationAgent       | GLM-5.1  |
| ReflectionAgent         | GLM-5.1  |
| ResponseAgent           | GLM-5.1  |
| CaseAgent               | Nemotron |
| EventInvestigationAgent | Nemotron |

---

# Request Routing Strategy

## Simple Requests

Examples:

```text
Show my appointments

What is my claim status?

Do I have a refill pending?
```

Route:

```text
GLM-5.1 Only
```

---

## Complex Requests

Examples:

```text
Why was my claim denied?

What caused my balance increase?

Explain everything that happened in my case.
```

Route:

```text
Nemotron
```

---

# Cost Optimization Strategy

Avoid sending every request to Nemotron.

Bad:

```text
All requests
      ↓
Nemotron
```

Good:

```text
Intent Agent
      ↓
Planner Agent
      ↓
Simple → GLM

Complex → Nemotron
```

---

# Structured Output Strategy

Every agent must return JSON.

Example:

```json
{
  "intent": "billing",
  "confidence": 0.95
}
```

Never allow free-form outputs between agents.

---

# JSON Enforcement

Use:

```python
response_format={
    "type": "json_object"
}
```

or

```python
PydanticOutputParser
```

for all internal agent communication.

---

# Verification Pipeline

All specialist outputs pass through VerificationAgent.

Workflow:

```text
Specialist Agent
        ↓
Verification Agent
        ↓
PASS
        ↓
Continue
```

---

# Verification Responsibilities

Check:

```text
Unsupported Claims

Hallucinations

Missing Evidence

Contradictions

Invalid References
```

Output:

```json
{
  "status": "PASS",
  "issues": []
}
```

---

# Reflection Pipeline

Reflection Agent evaluates completeness.

Workflow:

```text
Verification
      ↓
Reflection
      ↓
Response
```

Questions:

```text
Did we answer everything?

Is information missing?

Should we re-plan?
```

---

# Replanning Strategy

If ReflectionAgent detects missing information:

```text
Reflection
      ↓
Planner
      ↓
Additional Agents
      ↓
Verification
      ↓
Reflection
```

---

# Prompt Management

Prompts are stored outside source code.

Directory:

```text
app/
└── llm/
    └── prompts/
```

Files:

```text
authorization.md

risk.md

intent.md

planner.md

appointment.md

billing.md

insurance.md

refill.md

case.md

event_investigation.md

verification.md

reflection.md

response.md
```

---

# Prompt Versioning

Every prompt must have a version.

Examples:

```text
intent_v1

intent_v2

event_v1

event_v2
```

Audit logs must store prompt versions.

Example:

```json
{
  "agent": "EventInvestigationAgent",
  "prompt_version": "event_v2"
}
```

---

# RAG Integration

Pinecone is used only for knowledge retrieval.

Examples:

```text
Clinic Policies

Insurance Policies

Patient Education

FAQs

Provider Guidelines
```

---

# RAG Workflow

```text
Question
      ↓
Retriever
      ↓
Pinecone
      ↓
Relevant Chunks
      ↓
Agent
      ↓
Response
```

---

# Hybrid Data Strategy

MongoDB:

```text
Operational Data
```

Examples:

```text
Patients

Appointments

Claims

Billing

Events
```

Pinecone:

```text
Knowledge Data
```

Examples:

```text
Policies

FAQs

Guidelines
```

---

# Context Assembly

Before sending a request to a model:

Gather:

```text
Patient Context

Events

Claims

Appointments

Policy Documents

Conversation History
```

Then construct final prompt.

---

# Long Context Strategy

For Patient 360 analysis:

Retrieve:

```text
Recent Events

Claims

Billing Records

Case History
```

Summarize if context exceeds limits.

---

# Model Fallback Strategy

If Nemotron fails:

```text
Nemotron
     ↓
Retry
     ↓
Fallback
     ↓
GLM-5.1
```

Log fallback in audit records.

---

# Observability

Track:

```text
Token Usage

Prompt Version

Latency

Cost

Failure Rate

Escalation Rate
```

Store:

```text
audit_logs
```

and

```text
agent_metrics
```

---

# Response Generation Strategy

ResponseAgent receives:

```text
Specialist Results

Verification Results

Reflection Results
```

Generates:

```text
Patient-Friendly Explanation
```

Rules:

* Simple language
* No diagnosis
* No medication advice
* Evidence-based responses

---

# Future Model Expansion

Potential additions:

```text
Llama 4

Qwen 3

DeepSeek

Claude

GPT Models
```

through a unified model interface.

---

# Recommended MVP Strategy

Use:

```text
GLM-5.1

Nemotron-3 Super 120B A12B

MongoDB

Redis
```

Do not introduce multiple LLM providers initially.

Keep architecture simple.

---

# Final Principle

Use the smallest, fastest, cheapest model that can safely complete the task.

Reserve large reasoning models only for:

* Case Analysis
* Timeline Investigation
* Event Correlation
* Root Cause Analysis

This approach provides the best balance between cost, performance, scalability, and explainability for the PatientCare Platform.
