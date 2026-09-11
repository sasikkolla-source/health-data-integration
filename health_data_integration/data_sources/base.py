"""
base.py
-------
Every integration (wearable device, manual entry form, lab system, a real
EHR/FHIR endpoint, etc.) implements this interface. As long as an adapter
returns a list of normalized dicts shaped like NORMALIZED_FIELDS, the rest
of the app doesn't care where the data came from. This is the key
"integration" pattern of the project: heterogeneous sources -> one schema.
"""

from abc import ABC, abstractmethod

NORMALIZED_FIELDS = {"source", "metric", "value", "unit", "recorded_at"}


class HealthDataSource(ABC):
    source_name: str = "unknown"

    @abstractmethod
    def fetch(self, patient_name: str) -> list[dict]:
        """Return a list of normalized health record dicts for the patient."""
        raise NotImplementedError

    def _record(self, metric: str, value: float, unit: str, recorded_at: str) -> dict:
        return {
            "source": self.source_name,
            "metric": metric,
            "value": value,
            "unit": unit,
            "recorded_at": recorded_at,
        }
