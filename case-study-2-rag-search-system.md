# Case Study — An End-to-End RAG Search & Recommendation System: From Query Understanding to Ranking

> Korean home-appliance manufacturer | ML Engineer (owned search & ranking nodes) | Mar–Sep 2025
> *Details are generalized for client confidentiality; all diagrams and figures are reconstructed.*

## 1. Context

When a quality issue occurred on the manufacturing floor, engineers manually searched past cases for similar issues and resolutions. The goal: a Teams chatbot that searches and recommends historical quality issues and their fixes.

## 2. Designing the search funnel

A single vector search wasn't enough — user queries ranged from part-keyword lookups to free-form symptom descriptions. With LangGraph, I split the funnel into explicit nodes:

```
User query
   → [Intent classification]  Query-type detection (Few-shot + CoT)
   → [Retrieval]              Per-type index routing, hybrid search
   → [Ranking]                Business-priority ordering
   → Response generation
```

**Query understanding** — Few-shot intent–query pairs in the system prompt, with CoT rationale output to improve classification quality. LangGraph state management injected context dynamically based on the classified intent.

**Retrieval** — 3 purpose-built indices (keyword, class, full-text) with text-embedding-3-large embeddings; HNSW parameters and index configurations selected through comparative experiments.

**Ranking** — Similarity alone couldn't satisfy the business need of "most important cases first." I designed and implemented business-priority ranking combining importance, recency, and acceptance-rate signals. (My owned area.)

## 3. Deciding retrieval quality by experiment, not intuition

| Candidate | Method |
|---|---|
| Simple | Keyword matching |
| Semantic | Semantic re-ranking |
| Full | Full-text search |
| Hybrid | Vector + keyword combined |

Evaluating each mode on a common query set, the hybrid configuration won. Cosine-similarity semantic retrieval caught "same symptom, different wording" cases the legacy keyword system missed.

## 4. Crisis response: zero-downtime index redesign

Mid-project, the client's source data schema changed. I led a month-long index redesign and full re-ingestion, completing the migration without service interruption.

## 5. Operations

- Prompts version-controlled in Azure DevOps like source code — reproducible experiments
- AKS-based CI/CD; ingestion monitoring and log analysis via kubectl
- FastAPI + Streamlit serving

## 6. Results

- 100% UAT pass on owned modules (96%+ overall)
- Client-defined KPI (work-hours saved) achieved — the manual search process replaced by the chatbot
- Semantic retrieval substantially outperformed the legacy keyword search

## 7. Lessons

- Search quality is the product of the whole funnel (query understanding → retrieval → ranking), not one model. The biggest gain came from the ranking layer — users don't want "similar documents," they want "the document to act on now."
- Prompts are code. Without version control, you can't debug "it worked last week."
