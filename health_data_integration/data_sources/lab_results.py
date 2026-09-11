"""
lab_results.py
--------------
Simulates an integration with a clinical laboratory system
(e.g. an HL7/FHIR "Observation" feed). Real implementations would
parse lab result messages/files; here we generate representative values.
"""

import random
from datetime import datetime, timedelta

from .base import HealthDataSource


class LabResultsDataSource(HealthDataSource):
    source_name = "lab"

    def fetch(self, patient_name: str) -> list[dict]:
        ts = (datetime.utcnow() - timedelta(days=3)).isoformat()
        return [
            self._record(
                "cholesterol_total", round(random.uniform(150, 220), 1), "mg/dL", ts
            ),
            self._record(
                "glucose_fasting", round(random.uniform(80, 115), 1), "mg/dL", ts
            ),
            self._record("hba1c", round(random.uniform(4.8, 6.2), 1), "%", ts),
        ]
