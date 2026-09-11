# Health Data Integration

A simple base project that demonstrates integrating health data from
multiple heterogeneous sources into one unified record store and dashboard.

## What it integrates

| Source | Represents | Metrics |
|---|---|---|
| `wearable` | Fitness tracker / smartwatch API (Fitbit, Apple Health, Google Fit style) | heart_rate, steps, sleep_hours |
| `manual` | Data typed in directly by a patient/clinician | weight_kg, systolic_bp, diastolic_bp |
| `lab` | Clinical lab system (HL7/FHIR Observation style) | cholesterol_total, glucose_fasting, hba1c |

Each source is a small adapter (`data_sources/*.py`) that implements a common
`fetch(patient_name) -> list[dict]` interface and returns data already
normalized into one shape:

```json
{ "source": "wearable", "metric": "heart_rate", "value": 72.5, "unit": "bpm", "recorded_at": "2026-09-06T10:00:00" }
```

That's the core integration pattern: no matter how different the upstream
APIs are, everything lands in the same schema before it's stored, so the
database, API, and dashboard never need source-specific logic.

## Project structure

```
health_data_integration/
├── app.py                  # Flask app: routes + API
├── database.py              # SQLite schema + helper functions
├── data_sources/
│   ├── base.py               # Shared adapter interface
│   ├── wearable.py            # Simulated fitness tracker feed
│   ├── manual_entry.py        # Manual/form-based entries
│   └── lab_results.py         # Simulated lab system feed
├── templates/index.html     # Dashboard page
├── static/style.css         # Dashboard styling
├── static/script.js         # Dashboard logic (fetch/sync/render)
└── requirements.txt
```

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000**.

1. Type a patient name and click **Sync All Sources** — this pulls from the
   wearable, manual, and lab adapters and stores normalized records.
2. Add an extra manual reading (weight/blood pressure) any time.
3. The unified table and summary cards update from `/api/patients/<id>/records`,
   showing data from all sources side by side.

## API endpoints

- `GET  /api/sources` — list registered data sources
- `GET  /api/patients` — list known patients
- `POST /api/sync` — `{ "patient_name": "..." }` → pulls & stores from every source
- `POST /api/manual-entry` — `{ "patient_name", "weight_kg", "systolic_bp", "diastolic_bp" }`
- `GET  /api/patients/<id>/records` — unified record list for a patient

## Extending it

To add a real integration (e.g. an actual Fitbit or FHIR endpoint):

1. Create a new file in `data_sources/`, subclass `HealthDataSource`.
2. Implement `fetch()` to call the real API and return normalized records
   via `self._record(metric, value, unit, recorded_at)`.
3. Register the new adapter in `data_sources/__init__.py`'s `ALL_SOURCES` list.

No changes are needed anywhere else — the database, API, and dashboard
work with any source that follows the shared schema.
