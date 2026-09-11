"""
data_sources package
---------------------
Exposes ALL_SOURCES: the registry of every integration the app knows
about, and integrate_patient(): the function that pulls from all of
them and normalizes results into one list, ready to persist.
"""

from .wearable import WearableDataSource
from .manual_entry import ManualEntryDataSource
from .lab_results import LabResultsDataSource

ALL_SOURCES = [
    WearableDataSource(),
    ManualEntryDataSource(),
    LabResultsDataSource(),
]


def integrate_patient(patient_name: str) -> list[dict]:
    """Pull data for a patient from every registered source and merge it."""
    all_records = []
    for source in ALL_SOURCES:
        try:
            all_records.extend(source.fetch(patient_name))
        except Exception as exc:  # a single failing source shouldn't break the rest
            print(f"[integration warning] {source.source_name} failed: {exc}")
    return all_records
