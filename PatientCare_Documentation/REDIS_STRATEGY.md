# REDIS_STRATEGY.md

# PatientCare Platform Redis Strategy

## Overview

Redis serves as the high-speed caching and state management layer for the PatientCare Platform.

Redis improves:

* Response Time
* Agent Performance
* LangGraph Execution
* Session Management
* Cost Optimization
* Scalability

Redis is NOT a source of truth.

MongoDB remains the primary operational database.

---

# Redis Architecture

```text
Patient
   │
   ▼
FastAPI
   │
   ▼
Redis
   │
 ┌─┼───────────────────┐
 ▼ ▼                   ▼
Session Cache    Agent State
Prompt Cache     Response Cache
Context Cache    Rate Limiting
```

---

# Why Redis?

Without Redis:

```text
Patient Query
      │
      ▼
MongoDB
      │
      ▼
LLM
```

Every request:

* Reads MongoDB
* Rebuilds context
* Rebuilds prompts

Higher latency.

Higher cost.

---

With Redis:

```text
Patient Query
      │
      ▼
Redis Cache
      │
      ▼
LLM
```

Much faster.

---

# Redis Use Cases

## Session Management

Stores active user sessions.

Key:

```text
session:{patient_id}
```

Example:

```json
{
  "patient_id": "PAT001",
  "role": "patient",
  "expires_at": "2026-06-20T10:00:00Z"
}
```

TTL:

```text
30 minutes
```

---

## LangGraph State Cache

Stores graph execution state.

Key:

```text
graph:{request_id}
```

Example:

```json
{
  "current_node": "BillingAgent",
  "execution_status": "running"
}
```

TTL:

```text
24 hours
```

---

## Context Cache

Stores recently assembled patient context.

Key:

```text
context:{patient_id}
```

Example:

```json
{
  "active_claims": [],
  "upcoming_appointments": [],
  "recent_events": []
}
```

TTL:

```text
10 minutes
```

---

## Response Cache

Stores common responses.

Key:

```text
response:{query_hash}
```

Example:

```text
What are clinic hours?
```

TTL:

```text
1 hour
```

---

## Prompt Cache

Stores generated prompts.

Key:

```text
prompt:{hash}
```

Purpose:

Avoid prompt reconstruction.

TTL:

```text
24 hours
```

---

# Agent State Management

Every agent execution can be checkpointed.

Example:

```json
{
  "request_id": "REQ001",
  "agent": "InsuranceAgent",
  "status": "running"
}
```

Key:

```text
agent:{request_id}
```

---

# Conversation Memory

Stores recent conversation history.

Key:

```text
chat:{patient_id}
```

Example:

```json
[
  {
    "role": "user",
    "content": "Why was my claim denied?"
  }
]
```

TTL:

```text
24 hours
```

---

# Rate Limiting

Prevent abuse.

---

## Chat Endpoint

```text
60 requests/minute
```

Key:

```text
rate_limit:chat:{user_id}
```

---

## Login Endpoint

```text
5 requests/minute
```

Key:

```text
rate_limit:login:{ip}
```

---

## Admin APIs

```text
20 requests/minute
```

Key:

```text
rate_limit:admin:{user_id}
```

---

# Distributed Locks

Prevent duplicate processing.

Example:

```text
claim investigation
```

Key:

```text
lock:{claim_id}
```

TTL:

```text
60 seconds
```

---

# Timeline Cache

Patient 360 timelines are expensive to build.

Cache result.

Key:

```text
timeline:{patient_id}
```

TTL:

```text
5 minutes
```

---

# Billing Cache

Cache read-only billing summaries.

Key:

```text
billing_summary:{patient_id}
```

TTL:

```text
2 minutes
```

Never cache write operations.

---

# Claim Cache

Cache claim lookups.

Key:

```text
claim:{claim_id}
```

TTL:

```text
2 minutes
```

---

# What Should NOT Be Cached

Never cache:

```text
Payment Transactions

Prescription Changes

Claim Updates

Appointment Updates

Security Decisions
```

Always read from MongoDB.

---

# Redis Data Structures

## Strings

Use for:

```text
Sessions

Prompt Cache

Response Cache
```

---

## Hashes

Use for:

```text
Patient Context

Agent State
```

---

## Lists

Use for:

```text
Conversation History

Event Buffers
```

---

## Sets

Use for:

```text
Active Sessions

Online Users
```

---

# Redis Key Naming Convention

```text
session:{patient_id}

context:{patient_id}

graph:{request_id}

claim:{claim_id}

timeline:{patient_id}

prompt:{hash}

response:{hash}
```

---

# Production Deployment

Recommended:

## AWS

```text
ElastiCache Redis
```

---

## Alternative

```text
Redis Cloud
```

---

# Redis Security

Requirements:

```text
TLS Enabled

Private Networking

Authentication Required

No Public Access
```

---

# Monitoring

Track:

```text
Memory Usage

Hit Rate

Miss Rate

Latency

Connections
```

---

# Recommended TTL Values

| Cache Type  | TTL    |
| ----------- | ------ |
| Session     | 30 min |
| Context     | 10 min |
| Timeline    | 5 min  |
| Prompt      | 24 hr  |
| Response    | 1 hr   |
| Agent State | 24 hr  |

---

# Redis Benefits

* Faster Responses
* Reduced MongoDB Load
* Lower LLM Costs
* Improved User Experience
* Better Scalability
* Faster LangGraph Execution

---

# Design Principle

```text
MongoDB = Source of Truth

Redis = Performance Layer
```

Never treat Redis as a database.

Always assume Redis data can disappear at any time.
