async function runCheck() {
  const username = document.getElementById("searchInput").value;

  const res = await fetch("/api/check/", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username})
  });

  const data = await res.json();
  renderResults(data.profiles);
  renderGraph(data.graph);
}

function renderResults(profiles) {
  const el = document.getElementById("results");
  el.innerHTML = "";

  profiles.forEach(p => {
    el.innerHTML += `
      <div class="card ${p.threat}">
        <h3>${p.platform}</h3>
        <p>${p.username}</p>
        <span>Threat: ${p.threat}</span>
        <p>Topics: ${p.topics.join(", ")}</p>
      </div>
    `;
  });
}
