"""
app.py
------
Health Data Integration - simple base project.

Flow:
  1. User enters a patient name and clicks "Sync All Sources".
  2. The app pulls data from every registered source (wearable device,
     manual entries, lab results), normalizes it into one schema, and
     stores it in SQLite.
  3. The dashboard fetches the unified record set via /api/patients/<id>/records
     and renders it as a grouped table + simple chart.

Run with:  python app.py
Then open: http://localhost:5000
"""

from flask import Flask, jsonify, render_template, request

import database
from data_sources import integrate_patient, ALL_SOURCES
from data_sources.manual_entry import ManualEntryDataSource

app = Flask(__name__)
database.init_db()


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/sources")
def api_sources():
    """List which data sources are wired into the integration."""
    return jsonify([s.source_name for s in ALL_SOURCES])


@app.route("/api/patients")
def api_list_patients():
    return jsonify(database.list_patients())


@app.route("/api/sync", methods=["POST"])
def api_sync():
    """
    Trigger integration for a patient: pull from every source and store
    the normalized results. Body: {"patient_name": "Jane Doe"}
    """
    payload = request.get_json(force=True) or {}
    patient_name = (payload.get("patient_name") or "").strip()
    if not patient_name:
        return jsonify({"error": "patient_name is required"}), 400

    patient_id = database.get_or_create_patient(patient_name)
    records = integrate_patient(patient_name)
    database.insert_records(patient_id, records)

    return jsonify(
        {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "records_synced": len(records),
        }
    )


@app.route("/api/manual-entry", methods=["POST"])
def api_manual_entry():
    """
    Accept a manual health entry submitted from the dashboard form and
    fold it into the same unified store as the other sources.
    Body: {"patient_name": "...", "weight_kg": .., "systolic_bp": .., "diastolic_bp": ..}
    """
    payload = request.get_json(force=True) or {}
    patient_name = (payload.get("patient_name") or "").strip()
    if not patient_name:
        return jsonify({"error": "patient_name is required"}), 400

    patient_id = database.get_or_create_patient(patient_name)
    manual = ManualEntryDataSource()
    records = manual.fetch_from_form(payload)
    database.insert_records(patient_id, records)

    return jsonify({"patient_id": patient_id, "records_added": len(records)})


@app.route("/api/patients/<int:patient_id>/records")
def api_patient_records(patient_id):
    records = database.get_records_for_patient(patient_id)
    return jsonify(records)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
