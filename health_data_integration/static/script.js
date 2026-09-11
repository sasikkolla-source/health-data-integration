let currentPatientId = null;

async function refreshPatientList(selectId) {
  const res = await fetch("/api/patients");
  const patients = await res.json();
  const select = document.getElementById("patientSelect");
  select.innerHTML = '<option value="">-- choose an existing patient --</option>';
  patients.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = p.name;
    if (p.id === selectId) opt.selected = true;
    select.appendChild(opt);
  });
}

async function syncPatient() {
  const name = document.getElementById("patientName").value.trim();
  const status = document.getElementById("syncStatus");
  if (!name) {
    status.textContent = "Enter a patient name first.";
    return;
  }
  status.textContent = "Syncing wearable, manual, and lab sources...";

  const res = await fetch("/api/sync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patient_name: name }),
  });
  const data = await res.json();

  if (!res.ok) {
    status.textContent = "Error: " + (data.error || "sync failed");
    return;
  }

  currentPatientId = data.patient_id;
  status.textContent = `Synced ${data.records_synced} records for ${data.patient_name}.`;
  await refreshPatientList(currentPatientId);
  await loadRecords();
}

async function submitManualEntry() {
  const name =
    document.getElementById("patientSelect").selectedOptions[0]?.textContent !==
    "-- choose an existing patient --"
      ? document.getElementById("patientSelect").selectedOptions[0]?.textContent
      : document.getElementById("patientName").value.trim();

  const status = document.getElementById("manualStatus");
  if (!name) {
    status.textContent = "Select or sync a patient first.";
    return;
  }

  const payload = {
    patient_name: name,
    weight_kg: document.getElementById("weight").value,
    systolic_bp: document.getElementById("systolic").value,
    diastolic_bp: document.getElementById("diastolic").value,
  };

  const res = await fetch("/api/manual-entry", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();

  if (!res.ok) {
    status.textContent = "Error: " + (data.error || "entry failed");
    return;
  }

  status.textContent = `Added ${data.records_added} manual record(s).`;
  currentPatientId = data.patient_id;
  await refreshPatientList(currentPatientId);
  await loadRecords();
}

async function loadRecords() {
  const select = document.getElementById("patientSelect");
  const id = select.value || currentPatientId;
  if (!id) return;
  currentPatientId = Number(id);

  const res = await fetch(`/api/patients/${id}/records`);
  const records = await res.json();
  renderSummary(records);
  renderTable(records);
}

function renderSummary(records) {
  const container = document.getElementById("summaryCards");
  container.innerHTML = "";
  const latestByMetric = {};
  records.forEach((r) => {
    latestByMetric[r.metric] = r; // records are ASC by time, so last write wins = latest
  });

  const highlight = ["heart_rate", "steps", "weight_kg", "glucose_fasting"];
  highlight.forEach((metric) => {
    const r = latestByMetric[metric];
    if (!r) return;
    const card = document.createElement("div");
    card.className = "metric-card";
    card.innerHTML = `<span class="label">${metric.replace(/_/g, " ")}</span>
                       <span class="value">${r.value} ${r.unit}</span>`;
    container.appendChild(card);
  });
}

function renderTable(records) {
  const tbody = document.querySelector("#recordsTable tbody");
  tbody.innerHTML = "";
  records
    .slice()
    .reverse()
    .forEach((r) => {
      const tr = document.createElement("tr");
      tr.className = `source-${r.source}`;
      const when = new Date(r.recorded_at).toLocaleString();
      tr.innerHTML = `<td>${r.source}</td><td>${r.metric}</td><td>${r.value}</td><td>${r.unit}</td><td>${when}</td>`;
      tbody.appendChild(tr);
    });
}

refreshPatientList();
