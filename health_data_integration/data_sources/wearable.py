"""
wearable.py
-----------
Simulates pulling data from a fitness tracker / smartwatch API
(e.g. Fitbit, Apple Health, Google Fit). In a real integration this
would call the vendor's REST API with OAuth credentials instead of
generating synthetic readings.
"""

import random
from datetime import datetime, timedelta

from .base import HealthDataSource


class WearableDataSource(HealthDataSource):
    source_name = "wearable"

    def fetch(self, patient_name: str) -> list[dict]:
        now = datetime.utcnow()
        records = []
        for i in range(5):
            ts = (now - timedelta(hours=i * 4)).isoformat()
            records.append(
                self._record("heart_rate", round(random.uniform(60, 95), 1), "bpm", ts)
            )
            records.append(
                self._record("steps", random.randint(500, 3000), "steps", ts)
            )
            records.append(
                self._record(
                    "sleep_hours", round(random.uniform(5.5, 8.5), 1), "hours", ts
                )
            )
        return records
