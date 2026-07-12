# Case Study — Refactoring a Large-Scale ML Batch Pipeline: ~99% Reduction in Airflow Worker Occupancy

> Global electronics company, marketing data organization | ML Engineer (led refactoring & optimization) | 2026
> *Details are generalized for client confidentiality; all diagrams and figures are reconstructed.*

## 1. Context

The client operated dozens of ML models for marketing campaigns on GCP. Cloud Composer (Airflow) orchestrated the batches; model training and inference ran as Vertex AI Custom Jobs.

## 2. Problems

Taking over operations, I found three structural issues.

**(1) Wasted worker resources** — Polling tasks that watched Vertex AI Jobs held an Airflow worker slot until the job finished: 2–12 hours per model. As concurrent batches grew, workers filled up with polling tasks while real work queued.

**(2) Duplicated code** — The same utility functions were copy-pasted across 5+ DAG files, with configuration hard-coded per file. One change meant N file edits.

**(3) No tests** — There was no test environment; every change deployed straight to production.

## 3. Approach

### 3-1. Worker occupancy: polling → reschedule-mode sensors

I compared Airflow's two sensor modes:

| Mode | Behavior | Worker slot |
|---|---|---|
| poke (equivalent to the legacy polling) | Holds the slot while waiting | Occupied for the entire job |
| reschedule | Checks, releases the slot, re-schedules the next check | Occupied only at check time |

I migrated polling tasks to `VertexAICustomJobSensor(mode='reschedule')`.
Trade-off considered: reschedule can delay completion detection by up to one poke interval. Since target jobs run for hours, minute-level delay was immaterial — and the freed worker slots were decisive.

### 3-2. Structure: shared modules + a DAG factory

- Extracted duplicated functions into 5 shared modules (config, Vertex AI, BigQuery, GCS, Airflow utils)
- Unified near-identical weekly DAGs with a `DAGConfig` dataclass + factory pattern — new batches now require only a config object
- Sequenced training-then-inference to eliminate OOM from concurrent execution

### 3-3. Tests: local, without GCP

GCP dependencies were woven through the code, making local testing impossible. I designed a `sys.modules` patching approach to mock the GCP SDKs, wrote 57 unit tests, and the pattern was adopted as the team standard.

## 4. Results

| Item | Before | After |
|---|---|---|
| Worker occupancy (polling) | 2–12 h per job | Check-time only (~99% reduction) |
| Batch files | 7 files, duplicated functions | 5 files + one shared module |
| Tests | None (direct-to-prod) | 57 tests, runnable locally |

Verification across all 44 model tasks: 24 minutes, zero failures.

## 5. Lessons

- Much of what looks like an infrastructure-cost problem is an execution-model design problem. No worker scale-up was needed — one sensor mode change solved it.
- Tests are the precondition for refactoring. The 57 tests are what made structural change possible without production risk.
