"""
manual_entry.py
----------------
Represents data a patient or clinician types in directly (weight,
blood pressure, blood glucose from a home meter, etc.), rather than
data pulled automatically from a device or lab system.
"""

from datetime import datetime

from .base import HealthDataSource


class ManualEntryDataSource(HealthDataSource):
    source_name = "manual"

    def fetch(self, patient_name: str) -> list[dict]:
        now = datetime.utcnow().isoformat()
        # In a real app these values come from a submitted form, not fixed data.
        return [
            self._record("weight_kg", 72.4, "kg", now),
            self._record("systolic_bp", 122, "mmHg", now),
            self._record("diastolic_bp", 80, "mmHg", now),
        ]

    def fetch_from_form(self, form: dict) -> list[dict]:
        """Build records directly from a submitted web form."""
        now = datetime.utcnow().isoformat()
        records = []
        field_units = {
            "weight_kg": "kg",
            "systolic_bp": "mmHg",
            "diastolic_bp": "mmHg",
        }
        for field, unit in field_units.items():
            if form.get(field):
                records.append(self._record(field, float(form[field]), unit, now))
        return records
