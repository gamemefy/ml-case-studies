"""
Pattern: unit-testing cloud-dependent pipeline code locally, without cloud access.

Context
-------
A production ML codebase imported GCP SDKs at module top level, which made
local testing impossible — every change deployed straight to production.
Patching `sys.modules` *before* importing the code under test lets 57 unit
tests run anywhere (no credentials, no network), and became the team standard:
44 pipeline tasks verified in 24 minutes with zero failures.

Why not plain @mock.patch? Because the imports fail *at import time* —
you must install fakes into sys.modules before the module under test loads.

This file is a distilled, illustrative pattern (not tied to any client code).
"""

import sys
import types
import unittest
from unittest import mock

# ---------------------------------------------------------------------------
# 1) Install fake cloud SDK modules BEFORE importing the code under test.
# ---------------------------------------------------------------------------
FAKE_MODULES = [
    "google", "google.cloud", "google.cloud.bigquery",
    "google.cloud.storage", "google.cloud.aiplatform",
]

for name in FAKE_MODULES:
    sys.modules.setdefault(name, types.ModuleType(name))

# Give the fakes just enough surface for the import to succeed.
sys.modules["google.cloud.bigquery"].Client = mock.MagicMock(name="bigquery.Client")
sys.modules["google.cloud.storage"].Client = mock.MagicMock(name="storage.Client")

# Only now is this import safe on a laptop with no GCP credentials:
# from pipelines.common import bigquery_utils


# ---------------------------------------------------------------------------
# 2) Example code under test (inlined here so the file is self-contained).
# ---------------------------------------------------------------------------
def build_export_query(table: str, ds: str) -> str:
    """Pure logic — the majority of pipeline bugs live in code like this."""
    if not table.replace("_", "").isalnum():
        raise ValueError(f"suspicious table name: {table}")
    return f"SELECT * FROM `{table}` WHERE ds = '{ds}'"


def export_table(bq_client, table: str, ds: str) -> str:
    """Thin cloud wrapper: inject the client, keep logic testable."""
    query = build_export_query(table, ds)
    bq_client.query(query)
    return query


# ---------------------------------------------------------------------------
# 3) Tests: pure logic tested directly; cloud calls asserted via the fake.
# ---------------------------------------------------------------------------
class TestExport(unittest.TestCase):
    def test_query_contains_partition_filter(self):
        q = build_export_query("events_daily", "2026-07-01")
        self.assertIn("ds = '2026-07-01'", q)

    def test_rejects_suspicious_table_names(self):
        with self.assertRaises(ValueError):
            build_export_query("events; DROP TABLE x", "2026-07-01")

    def test_cloud_call_receives_built_query(self):
        fake_client = mock.MagicMock()
        q = export_table(fake_client, "events_daily", "2026-07-01")
        fake_client.query.assert_called_once_with(q)


if __name__ == "__main__":
    unittest.main()
