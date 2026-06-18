# PINECONE_STRATEGY.md

# Overview

Pinecone stores healthcare knowledge.

Pinecone does NOT store patient operational data.

---

# Store In Pinecone

* Clinic Policies
* Insurance Policies
* FAQs
* Patient Education
* Provider Guidelines
* Consent Documents
* SOP Documents

---

# Do NOT Store In Pinecone

* Patients
* Claims
* Billing
* Payments
* Appointments
* Events
* Refills

Store those in MongoDB.

---

# Namespaces

clinic_policies

insurance_policies

faq

patient_education

provider_guidelines

consent_documents

---

# Metadata Example

{
"doc_id": "INS001",
"title": "Insurance Guide",
"category": "insurance",
"tenant_id": "clinic_001"
}

---

# Ingestion Flow

PDF
↓
Text Extraction
↓
Chunking
↓
Embedding
↓
Pinecone

---

# Retrieval Flow

Question
↓
Embedding
↓
Vector Search
↓
Top K Chunks
↓
Response Agent

---

# Example

Question:

Does my insurance cover MRI?

MongoDB:

Patient Insurance Plan

Pinecone:

Insurance Policy Text

Combined Response

---

# Chunking Strategy

Chunk Size:

800–1200 tokens

Overlap:

100–150 tokens

---

# Top K

Recommended:

Top 5

Rerank:

Top 3

---

# Future Expansion

* Multilingual Policies
* Provider Knowledge Base
* Medical Education Material
* Internal Clinical SOP Search
