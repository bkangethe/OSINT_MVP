const searchBtn = document.getElementById("searchBtn");
const searchInput = document.getElementById("searchInput");
const platformFilter = document.getElementById("platformFilter");
const resultsContainer = document.getElementById("results");
const paginationContainer = document.getElementById("pagination");

searchBtn.addEventListener("click", async () => {
  const username = searchInput.value.trim();
  if (!username) return;
  resultsContainer.innerHTML = `<div class="progress">Searching...</div>`;
  paginationContainer.innerHTML = "";

  try {
    const response = await fetch("/api/check", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({username})
    });
    const data = await response.json();
    let filteredProfiles = data.profiles;
    const platform = platformFilter.value;
    if(platform!=="all") filteredProfiles = filteredProfiles.filter(p=>p.platform===platform);

    const pageSize = 6;
    let currentPage=1;

    function renderPage(page){
      resultsContainer.innerHTML="";
      const start=(page-1)*pageSize;
      const end=start+pageSize;
      filteredProfiles.slice(start,end).forEach(p=>{
        const card=document.createElement("div");
        card.className="card";
        const risk=p.nlp?.risk || "low";
        card.innerHTML=`
          <h2>${p.platform}</h2>
          <p>Username: ${p.username}</p>
          <span class="badge badge-${risk}">Risk: ${risk.toUpperCase()}</span>
          <a href="${p.url}" target="_blank">Visit Profile</a>
          <img class="thumbnail" src="${p.vision?.thumbnail_url || 'https://via.placeholder.com/150'}" alt="preview">
        `;
        resultsContainer.appendChild(card);
      });

      // Pagination buttons
      const totalPages=Math.ceil(filteredProfiles.length/pageSize);
      paginationContainer.innerHTML="";
      for(let i=1;i<=totalPages;i++){
        const btn=document.createElement("button");
        btn.textContent=i;
        btn.onclick=()=>renderPage(i);
        paginationContainer.appendChild(btn);
      }
    }

    renderPage(currentPage);

    // Render graph
    renderGraph(username);

  } catch(err){
    resultsContainer.innerHTML=`<div class="progress">Error: ${err.message}</div>`;
  }
});
