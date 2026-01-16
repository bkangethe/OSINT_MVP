const token = localStorage.getItem("token");

async function login() {
  const res = await fetch("/api/login", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      username: user.value,
      password: pass.value
    })
  });
  const data = await res.json();
  localStorage.setItem("token", data.token);
}

searchBtn.onclick = async () => {
  results.innerHTML = "Scanning…";
  const res = await fetch("/api/check", {
    method:"POST",
    headers:{
      "Content-Type":"application/json",
      "Authorization":"Bearer "+localStorage.getItem("token")
    },
    body:JSON.stringify({username: searchInput.value})
  });
  const data = await res.json();

  results.innerHTML="";
  data.profiles.forEach(p=>{
    results.innerHTML+=`
      <div class="card ${p.nlp.risk}">
        <h3>${p.platform}</h3>
        <p>${p.username}</p>
        <span>${p.nlp.risk.toUpperCase()}</span>
        <a href="${p.url}" target="_blank">Open</a>
      </div>`;
  });
};
