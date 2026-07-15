"""
Pattern: DAG factory + reschedule-mode sensors for ML batch pipelines.

Context
-------
In a production marketing-ML platform, near-identical weekly DAGs were
copy-pasted across 7 files, and polling tasks held Airflow worker slots for
the full duration of Vertex AI jobs (2-12 hours each). Two patterns fixed it:

1. A `DAGConfig` dataclass + factory — new batches are added by declaring a
   config object, not by copying a DAG file.
2. `mode="reschedule"` sensors — the worker slot is released between checks,
   cutting worker occupancy by ~99% for hour-scale jobs.

This file is a distilled, illustrative pattern (not tied to any client code).
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Provider import shown for illustration; adjust to your provider version.
# from airflow.providers.google.cloud.sensors.vertex_ai import VertexAICustomJobSensor


@dataclass(frozen=True)
class DAGConfig:
    """Everything that varies between batches lives here — nothing else does."""
    dag_id: str
    schedule: str                      # cron
    model_name: str
    train_machine_type: str = "e2-standard-8"   # right-size from measured usage
    poke_interval_s: int = 300                  # sensor check cadence
    retries: int = 3
    retry_delay_min: int = 5
    tags: list = field(default_factory=lambda: ["ml-batch"])


def submit_training(model_name: str, machine_type: str, **_):
    """Submit the Vertex AI custom job and push its ID to XCom."""
    ...


def run_inference(model_name: str, **_):
    """Runs only after training has fully completed (sequential to avoid OOM)."""
    ...


def build_dag(cfg: DAGConfig) -> DAG:
    """One factory, N batches. Adding a batch == adding a DAGConfig."""
    with DAG(
        dag_id=cfg.dag_id,
        schedule=cfg.schedule,
        start_date=datetime(2026, 1, 1),
        catchup=False,
        tags=cfg.tags,
        default_args={
            # Retries make transient failures (resource contention, slot
            # saturation) self-healing instead of pager duty.
            "retries": cfg.retries,
            "retry_delay": timedelta(minutes=cfg.retry_delay_min),
        },
    ) as dag:
        train = PythonOperator(
            task_id="submit_training",
            python_callable=submit_training,
            op_kwargs={"model_name": cfg.model_name,
                       "machine_type": cfg.train_machine_type},
        )

        # KEY PATTERN: mode="reschedule".
        # poke mode  -> holds a worker slot for the job's full 2-12 h duration.
        # reschedule -> checks, releases the slot, and is re-scheduled at the
        #               next poke_interval. Trade-off: completion detection can
        #               lag by up to one interval — irrelevant for hour-scale
        #               jobs, decisive for worker capacity.
        wait_training = VertexAICustomJobSensor(  # noqa: F821 (illustrative)
            task_id="wait_training",
            mode="reschedule",
            poke_interval=cfg.poke_interval_s,
        )

        inference = PythonOperator(
            task_id="run_inference",
            python_callable=run_inference,
            op_kwargs={"model_name": cfg.model_name},
        )

        train >> wait_training >> inference
    return dag


# ---------------------------------------------------------------------------
# Registration: each batch is one line of configuration.
# ---------------------------------------------------------------------------
CONFIGS = [
    DAGConfig(dag_id="ml_click_rate_weekly", schedule="0 3 * * 1", model_name="click_rate"),
    DAGConfig(dag_id="ml_open_rate_weekly",  schedule="0 4 * * 1", model_name="open_rate",
              train_machine_type="n1-highmem-32"),
]

for _cfg in CONFIGS:
    globals()[_cfg.dag_id] = build_dag(_cfg)
