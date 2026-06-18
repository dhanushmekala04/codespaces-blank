# DEPLOYMENT.md

# PatientCare Platform Deployment Guide

## Overview

This document describes how to deploy the PatientCare Platform using:

* Docker
* GitHub Actions
* AWS ECS Fargate
* Amazon ECR
* MongoDB Atlas
* Redis
* Application Load Balancer (ALB)

This architecture is designed for production workloads and supports horizontal scaling.

---

# Production Architecture

```text
                     Internet
                          │
                          ▼
               Application Load Balancer
                          │
                          ▼
                 ECS Service (Fargate)
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
        FastAPI Container      FastAPI Container
              │                       │
              └───────────┬───────────┘
                          │
                          ▼
                    LangGraph Agents
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
 MongoDB Atlas        Redis Cloud        Pinecone
```

---

# AWS Services

| Service         | Purpose           |
| --------------- | ----------------- |
| ECS Fargate     | Container Hosting |
| ECR             | Docker Registry   |
| ALB             | Load Balancing    |
| CloudWatch      | Logs & Metrics    |
| Secrets Manager | Secret Storage    |
| IAM             | Permissions       |
| VPC             | Networking        |

---

# Repository Structure

```text
PatientCare/
│
├── app/
├── docs/
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
│
└── .github/
    └── workflows/
        └── deploy.yml
```

---

# Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
```

---

# Build Docker Image

```bash
docker build -t patientcare .
```

---

# Run Locally

```bash
docker run -p 8000:8000 patientcare
```

---

# Environment Variables

Create:

```text
.env
```

Example:

```env
ENVIRONMENT=production

MONGODB_URI=

REDIS_URL=

PINECONE_API_KEY=

PINECONE_INDEX=

GLM_API_KEY=

NEMOTRON_API_KEY=

JWT_SECRET_KEY=

LANGFUSE_PUBLIC_KEY=

LANGFUSE_SECRET_KEY=
```

---

# AWS ECR

## Create Repository

Example:

```text
patientcare-backend
```

---

## Login to ECR

```bash
aws ecr get-login-password \
--region us-east-1 \
| docker login \
--username AWS \
--password-stdin \
xxxxxxxx.dkr.ecr.us-east-1.amazonaws.com
```

---

## Tag Image

```bash
docker tag patientcare:latest \
xxxxxxxx.dkr.ecr.us-east-1.amazonaws.com/patientcare-backend:latest
```

---

## Push Image

```bash
docker push \
xxxxxxxx.dkr.ecr.us-east-1.amazonaws.com/patientcare-backend:latest
```

---

# ECS Fargate

## Cluster

Create:

```text
patientcare-cluster
```

---

## Task Definition

```json
{
  "family": "patientcare",

  "cpu": "1024",

  "memory": "2048",

  "networkMode": "awsvpc",

  "requiresCompatibilities": [
    "FARGATE"
  ]
}
```

---

## Container

```json
{
  "name": "patientcare-api",

  "image": "ECR_IMAGE",

  "portMappings": [
    {
      "containerPort": 8000
    }
  ]
}
```

---

# ECS Service

Create:

```text
patientcare-service
```

Recommended:

```text
Desired Count = 2
```

This provides high availability.

---

# Auto Scaling

Scale based on:

```text
CPU Utilization

Memory Utilization

Request Count
```

Example:

```text
Min Tasks = 2

Max Tasks = 10
```

---

# Application Load Balancer

Create:

```text
patientcare-alb
```

---

# Listener

```text
443 HTTPS
```

Forward to:

```text
patientcare-target-group
```

---

# Health Check

Endpoint:

```http
GET /health
```

Expected:

```json
{
  "status": "healthy"
}
```

---

# MongoDB Atlas

Recommended:

```text
M10+
```

Collections:

```text
patients

appointments

claims

billing

events

audit_logs
```

---

# Redis

Recommended:

```text
Redis Cloud

or

AWS ElastiCache
```

Used For:

```text
Session Cache

Prompt Cache

Context Cache

Rate Limiting
```

---

# Pinecone

Namespaces:

```text
clinic_policies

insurance_policies

faq

patient_education

provider_guidelines
```

---

# AWS Secrets Manager

Store:

```text
MONGODB_URI

REDIS_URL

PINECONE_API_KEY

JWT_SECRET_KEY

GLM_API_KEY

NEMOTRON_API_KEY
```

Never store secrets in code.

---

# GitHub Actions CI/CD

File:

```text
.github/workflows/deploy.yml
```

---

# Workflow

```text
Push to Main
      │
      ▼
Run Tests
      │
      ▼
Build Docker Image
      │
      ▼
Push To ECR
      │
      ▼
Deploy ECS Service
```

---

# Example Workflow

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:

  deploy:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -r requirements.txt

      - run: pytest

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - uses: aws-actions/amazon-ecr-login@v2

      - run: |
          docker build -t patientcare .

      - run: |
          docker tag patientcare:latest \
          ${{ secrets.ECR_REPOSITORY }}:latest

      - run: |
          docker push \
          ${{ secrets.ECR_REPOSITORY }}:latest

      - run: |
          aws ecs update-service \
          --cluster patientcare-cluster \
          --service patientcare-service \
          --force-new-deployment
```

---

# GitHub Secrets

Configure:

```text
AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY

ECR_REPOSITORY
```

---

# Logging

Send logs to:

```text
AWS CloudWatch
```

Capture:

```text
API Requests

Agent Execution

Errors

Token Usage

Latency
```

---

# Production Health Endpoints

## Liveness

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

## Readiness

```http
GET /ready
```

Checks:

```text
MongoDB

Redis

Pinecone
```

---

# Deployment Environments

## Development

```text
Local Docker
```

---

## Staging

```text
AWS ECS
```

Smaller resources.

---

## Production

```text
AWS ECS Fargate
```

Multi-AZ deployment.

---

# Production Checklist

```text
Dockerized

CI/CD Enabled

ECR Configured

ECS Service Running

ALB Configured

HTTPS Enabled

MongoDB Connected

Redis Connected

Secrets Manager Configured

CloudWatch Enabled

Auto Scaling Enabled
```

---

# Recommended MVP Infrastructure

```text
FastAPI

LangGraph

MongoDB Atlas

Redis Cloud

AWS ECS Fargate

Amazon ECR

GitHub Actions

CloudWatch
```

This setup is simple, scalable, cost-efficient, and strong enough for a production-grade Patient 360 Agentic AI platform.
