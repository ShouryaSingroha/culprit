const METRICS = ["cpu", "memory", "disk", "network"];
const charts = {};
const openIncidents = new Set();

function incidentKey(inc) {
  return inc.time + "-" + inc.metric;
}

function format(metric, v) {
  if (v === undefined) return "-";
  return metric === "cpu" || metric === "memory"
    ? v.toFixed(0) + "%"
    : v.toFixed(1) + " MB/s";
}

for (const metric of METRICS) {
  charts[metric] = new Chart(document.getElementById("chart-" + metric), {
    type: "line",
    data: { labels: [], datasets: [{ data: [], borderWidth: 1.5, pointRadius: 0, tension: 0.25 }] },
    options: {
      animation: false,
      plugins: { legend: { display: false } },
      scales: { x: { display: false }, y: { beginAtZero: true } },
    },
  });
}

async function refreshStats() {
  const data = await (await fetch("/api/stats")).json();
  for (const metric of METRICS) {
    const series = data[metric];
    document.getElementById("val-" + metric).textContent = format(metric, series[series.length - 1]);
    charts[metric].data.labels = data.timestamps;
    charts[metric].data.datasets[0].data = series;
    charts[metric].update();
  }
}

function incidentElement(inc) {
  const li = document.createElement("li");
  li.className = "incident";

  const summary = document.createElement("div");
  summary.textContent = `${inc.time}  ${inc.metric}  ${format(inc.metric, inc.value)} (normal ${format(inc.metric, inc.baseline)})`;
  li.appendChild(summary);

  const list = document.createElement("div");
  list.className = "suspects";
  for (const s of inc.suspects) {
    const row = document.createElement("div");
    row.textContent = `${s.name} (pid ${s.pid}): ${s.detail}`;
    list.appendChild(row);
  }
  li.appendChild(list);

  const key = incidentKey(inc);
  if (openIncidents.has(key)) li.classList.add("open");

  li.addEventListener("click", () => {
    li.classList.toggle("open");
    if (li.classList.contains("open")) openIncidents.add(key);
    else openIncidents.delete(key);
  });
  return li;
}

async function refreshIncidents() {
  const incidents = await (await fetch("/api/incidents")).json();
  const list = document.getElementById("incidents");
  list.replaceChildren(...incidents.map(incidentElement));
  document.getElementById("empty").hidden = incidents.length > 0;
}

setInterval(refreshStats, 1000);
setInterval(refreshIncidents, 3000);
refreshStats();
refreshIncidents();