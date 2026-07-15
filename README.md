# ML Engineering Case Studies & Notebooks — Donghyeok Im

Production ML/LLM engineering from enterprise projects, in two forms: **case studies** (problem → approach → trade-offs → results) and **runnable notebooks & code patterns** that reconstruct the key techniques on synthetic data. All client-specific details are generalized; no proprietary code, data, or documents are included.

엔터프라이즈 프로젝트의 프로덕션 ML/LLM 엔지니어링을 **케이스 스터디**(문제 → 접근 → 트레이드오프 → 결과)와 **실행 가능한 노트북·코드 패턴**(합성 데이터로 핵심 기법 재구성)으로 정리했습니다. 고객사 관련 정보는 모두 일반화했습니다.

## 📓 Notebooks

| Notebook | What it shows |
|---|---|
| [pairwise-llm-evaluation](./notebooks/pairwise-llm-evaluation.ipynb) | Replacing generate-then-score with single-stage pairwise LLM evaluation: position-bias mitigation, win-rate aggregation, and validating the evaluator against real-world outcomes (agreement, top-k hit rate) |
| [hybrid-search-comparison](./notebooks/hybrid-search-comparison.ipynb) | Keyword vs. semantic vs. hybrid (RRF) retrieval decided by experiment (Recall@K, MRR), plus deterministic business-priority re-ranking |
| [intent-classification-fewshot](./notebooks/intent-classification-fewshot.ipynb) | Query understanding for agent routing: closed intent set, structured output, few-shot + reason, measured zero-shot vs. few-shot |

## 📄 Case Studies

| # | Title | Highlights | EN | KR |
|---|---|---|---|---|
| 1 | Refactoring a Large-Scale ML Batch Pipeline | ~99% reduction in Airflow worker occupancy; 57 unit tests as team standard; DAG factory pattern | [EN](./case-study-1-airflow-optimization.md) | [KR](./케이스스터디_1_Airflow_배치_최적화.md) |
| 2 | End-to-End RAG Search & Recommendation System | Query understanding → hybrid retrieval → business-priority ranking; retrieval quality decided by experiments; 100% UAT on owned modules | [EN](./case-study-2-rag-search-system.md) | [KR](./케이스스터디_2_RAG_검색시스템.md) |

## 🧩 Code Patterns

| Pattern | What it shows |
|---|---|
| [airflow_dag_factory.py](./patterns/airflow_dag_factory.py) | `DAGConfig` dataclass + factory for N batches from one file; `mode="reschedule"` sensors and the worker-occupancy trade-off |
| [testing_without_cloud.py](./patterns/testing_without_cloud.py) | Unit-testing cloud-dependent pipeline code locally via `sys.modules` fakes — runnable as-is (`python testing_without_cloud.py`) |

## About

AI Engineer with 4 years across LLM agent systems, production ML pipelines (GCP/Azure/AWS), and MLOps.
Currently AI Consultant at EY, Seoul.

- LinkedIn: [linkedin.com/in/im-donghyeok](https://www.linkedin.com/in/im-donghyeok)
- Email: im.donghyeok.42@gmail.com
