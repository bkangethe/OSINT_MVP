const searchBtn = document.getElementById("searchBtn");
const searchInput = document.getElementById("searchInput");
const platformFilter = document.getElementById("platformFilter");
const resultsContainer = document.getElementById("results");
const paginationContainer = document.getElementById("pagination");

searchBtn.addEventListener("click", async () => {
  const username = searchInput.value.trim();
  if (!username) return;

  resultsContainer.innerHTML = `
    <div class="col-span-full text-center text-gray-500">
      Searching...
    </div>
  `;
  paginationContainer.innerHTML = "";

  try {
    const response = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });

    const data_ = await response.json();
    let data = data_.data || {};

    const platform = platformFilter.value;

    let profiles = data.profiles || [];
    let posts = data.posts || [];

    if (platform !== "all") {
      profiles = profiles.filter(p => p.platform === platform);
      posts = posts.filter(p => p.platform === platform);
    }

    const pageSize = 6;
    let currentPage = 1;

    function renderPage(page) {
      resultsContainer.innerHTML = "";
      paginationContainer.innerHTML = "";

      const allItems = [
        ...profiles.map(p => ({ type: "profile", data: p })),
        ...posts.map(p => ({ type: "post", data: p }))
      ];

      const totalPages = Math.ceil(allItems.length / pageSize);
      const start = (page - 1) * pageSize;
      const end = start + pageSize;

      allItems.slice(start, end).forEach(item => {
        if (item.type === "profile") renderProfile(item.data);
        if (item.type === "post") renderPost(item.data);
      });

      for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement("button");
        btn.textContent = i;
        btn.className = `
          px-3 py-1 mx-1 rounded text-sm
          ${i === page ? "bg-indigo-600 text-white" : "bg-gray-200"}
        `;
        btn.onclick = () => renderPage(i);
        paginationContainer.appendChild(btn);
      }
    }

    function renderProfile(p) {
      const risk = p?.nlp?.risk || "low";

      const card = document.createElement("div");
      card.className = "bg-white p-4 rounded shadow";

      card.innerHTML = `
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
            ${p.platform}
          </span>
          <span class="text-xs px-2 py-1 rounded ${
            risk === "high"
              ? "bg-red-100 text-red-700"
              : risk === "medium"
              ? "bg-yellow-100 text-yellow-700"
              : "bg-green-100 text-green-700"
          }">
            Risk: ${risk.toUpperCase()}
          </span>
        </div>

        <h3 class="font-semibold">@${p.username || "unknown"}</h3>

        <a href="${p.url}" target="_blank"
           class="text-indigo-600 text-sm mt-2 inline-block">
          View Profile →
        </a>
      `;

      resultsContainer.appendChild(card);
    }

    function renderPost(post) {
      const risk = post?.nlp?.risk || "unknown";

      const card = document.createElement("div");
      card.className = "bg-white p-4 rounded shadow";

      card.innerHTML = `
        <div class="text-xs text-gray-500 flex justify-between">
          <span>${post.platform}</span>
          <span>${post.date || ""}</span>
        </div>

        <p class="mt-2 text-sm text-gray-800">
          ${post.text || "No content"}
        </p>

        <span class="inline-block mt-2 text-xs px-2 py-1 rounded ${
          risk === "high"
            ? "bg-red-100 text-red-700"
            : risk === "medium"
            ? "bg-yellow-100 text-yellow-700"
            : "bg-gray-100 text-gray-700"
        }">
          NLP: ${risk.toUpperCase()}
        </span>

        <a href="${post.url}" target="_blank"
           class="block text-indigo-600 text-sm mt-2">
          View Post →
        </a>
      `;

      resultsContainer.appendChild(card);
    }

    renderPage(currentPage);

  } catch (err) {
    resultsContainer.innerHTML = `
      <div class="col-span-full text-red-600 text-center">
        Error: ${err.message}
      </div>
    `;
  }
});
