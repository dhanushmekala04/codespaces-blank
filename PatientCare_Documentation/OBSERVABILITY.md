# OBSERVABILITY.md

# PatientCare Platform Observability Strategy

## Overview

Observability provides visibility into:

* API Performance
* Agent Execution
* LLM Usage
* Workflow Routing
* Database Operations
* Errors
* Latency
* Cost
* Human Escalations

Without observability, production AI systems become difficult to debug, monitor, and improve.

---

# Observability Goals

The platform must answer:

```text
What happened?

Why did it happen?

Where did it happen?

How much did it cost?

Which agent failed?

Which prompt caused the issue?

Which model generated the response?
```

---

# Architecture

```text
Patient Request
        │
        ▼
FastAPI
        │
        ▼
LangGraph
        │
        ▼
Agents
        │
        ▼
MongoDB / Redis / Pinecone
        │
        ▼
Observability Layer
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
Logs  Metrics Traces
```

---

# Observability Components

## Logging

Stores:

* Requests
* Responses
* Errors
* Agent Activity
* Escalations

---

## Metrics

Tracks:

* Latency
* Throughput
* Cost
* Token Usage

---

## Tracing

Tracks:

* End-to-End Workflow
* Agent Calls
* Tool Calls
* Database Queries

---

# Recommended Stack

## Application Monitoring

```text
OpenTelemetry
```

---

## Agent Tracing

```text
Langfuse
```

---

## Metrics

```text
Prometheus
```

---

## Dashboards

```text
Grafana
```

---

## Logs

```text
ELK Stack

or

OpenSearch
```

---

# Request Tracking

Every request gets a unique ID.

Example:

```json
{
  "request_id": "REQ001"
}
```

This ID follows the request through the entire workflow.

---

# Trace Flow

```text
REQ001
   │
   ▼
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
Billing Agent
   │
   ▼
Verification Agent
   │
   ▼
Response Agent
```

---

# Agent Metrics

Track for every agent:

```text
Execution Time

Token Usage

Prompt Version

Success Rate

Failure Rate

Retry Count
```

---

# Example Agent Record

```json
{
  "request_id": "REQ001",

  "agent": "BillingAgent",

  "prompt_version": "billing_v2",

  "model": "GLM-5.1",

  "execution_time_ms": 480,

  "input_tokens": 520,

  "output_tokens": 110,

  "status": "SUCCESS"
}
```

---

# API Metrics

Track:

```text
Requests Per Second

Average Latency

Error Rate

Success Rate

Active Users
```

---

# Example Metrics

```text
API Latency

P50 = 200ms

P95 = 750ms

P99 = 1500ms
```

---

# LLM Metrics

Track:

```text
Input Tokens

Output Tokens

Total Tokens

Prompt Cost

Completion Cost

Total Cost
```

---

# Example

```json
{
  "model": "Nemotron",

  "input_tokens": 3200,

  "output_tokens": 420,

  "cost_usd": 0.21
}
```

---

# LangGraph Workflow Tracing

Every graph node should be traced.

Example:

```text
AuthorizationAgent
      ↓
RiskAgent
      ↓
IntentAgent
      ↓
PlannerAgent
      ↓
InsuranceAgent
      ↓
EventInvestigationAgent
      ↓
VerificationAgent
      ↓
ResponseAgent
```

---

# Node-Level Metrics

Capture:

```text
Start Time

End Time

Duration

Status

Retries
```

---

# Tool Call Monitoring

Track:

```text
MongoDB Queries

Redis Reads

Redis Writes

Pinecone Searches

External API Calls
```

---

# MongoDB Metrics

Monitor:

```text
Query Time

Collection Usage

Connection Count

Index Efficiency
```

---

# Redis Metrics

Monitor:

```text
Cache Hit Rate

Cache Miss Rate

Memory Usage

Latency
```

---

# Pinecone Metrics

Monitor:

```text
Query Latency

Namespace Usage

Embedding Volume

Search Success Rate
```

---

# Agent Success Metrics

Measure:

```text
Intent Accuracy

Verification Pass Rate

Escalation Rate

Response Quality
```

---

# Human Escalation Metrics

Track:

```text
Escalations Per Day

Escalation Reasons

Resolution Time

Reviewer Workload
```

---

# Example

```json
{
  "reason": "Medication Advice",

  "count": 42,

  "avg_resolution_minutes": 12
}
```

---

# Error Monitoring

Track:

```text
LLM Failures

Database Failures

API Errors

Prompt Failures

Validation Errors
```

---

# Error Example

```json
{
  "request_id": "REQ001",

  "agent": "InsuranceAgent",

  "error_type": "MongoDBTimeout",

  "timestamp": "2026-06-19T12:00:00Z"
}
```

---

# Audit Metrics

Track:

```text
Patient Record Access

Claim Access

Billing Access

Document Access
```

---

# Security Monitoring

Track:

```text
Failed Logins

Permission Violations

Prompt Injection Attempts

Unauthorized Access Attempts
```

---

# Prompt Monitoring

Track:

```text
Prompt Version

Prompt Success Rate

Prompt Failure Rate

Token Usage
```

---

# Example

```json
{
  "prompt_version": "event_v2",

  "success_rate": 98.4
}
```

---

# Cost Monitoring

Track:

```text
Daily Cost

Per Agent Cost

Per User Cost

Per Workflow Cost
```

---

# Example

```json
{
  "workflow": "Claim Investigation",

  "average_cost": 0.12
}
```

---

# Dashboards

## Executive Dashboard

Track:

```text
Requests

Users

Costs

Escalations

Availability
```

---

## Engineering Dashboard

Track:

```text
Latency

Failures

Database Health

API Health

Tracing
```

---

## AI Dashboard

Track:

```text
Token Usage

Prompt Performance

Model Usage

Agent Success Rates
```

---

# Alerts

Create alerts for:

```text
API Error Rate > 5%

P95 Latency > 2s

Database Connection Failures

Escalation Spike

Model Failure Rate > 10%
```

---

# OpenTelemetry Integration

Instrument:

```text
FastAPI

LangGraph

MongoDB

Redis

Pinecone
```

---

# Langfuse Integration

Capture:

```text
Prompts

Responses

Token Usage

Agent Traces

Model Costs
```

---

# Retention Policy

Logs:

```text
90 Days
```

Metrics:

```text
1 Year
```

Audit Records:

```text
7 Years
```

Healthcare organizations may require longer retention periods.

---

# Production Readiness Checklist

```text
Request IDs Enabled

Distributed Tracing Enabled

Metrics Collection Enabled

Prompt Tracking Enabled

Cost Tracking Enabled

Alerts Configured

Dashboards Configured

Audit Logging Enabled
```

---

# Observability Goals

The platform should make it possible to:

* Trace every request
* Explain every AI decision
* Measure every cost
* Detect every failure
* Monitor every workflow

Observability is the foundation for operating a reliable Patient 360 Agentic AI platform in production.
