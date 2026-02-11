// const searchBtn = document.getElementById("searchBtn");
// const searchInput = document.getElementById("searchInput");
// const platformFilter = document.getElementById("platformFilter");
// const resultsContainer = document.getElementById("results");
// const paginationContainer = document.getElementById("pagination");

// searchBtn.addEventListener("click", async () => {
//   const username = searchInput.value.trim();
//   if (!username) return;

//   resultsContainer.innerHTML = `
//     <div class="col-span-full text-center text-gray-500">
//       Searching...
//     </div>
//   `;
//   paginationContainer.innerHTML = "";

//   try {
//     const response = await fetch("/api/check", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ username })
//     });

//     const data_ = await response.json();
//     let data = data_.data || {};

//     const platform = platformFilter.value;

//     let profiles = data.profiles || [];
//     let posts = data.posts || [];

//     if (platform !== "all") {
//       profiles = profiles.filter(p => p.platform === platform);
//       posts = posts.filter(p => p.platform === platform);
//     }

//     const pageSize = 6;
//     let currentPage = 1;

//     function renderPage(page) {
//       resultsContainer.innerHTML = "";
//       paginationContainer.innerHTML = "";

//       const allItems = [
//         ...profiles.map(p => ({ type: "profile", data: p })),
//         ...posts.map(p => ({ type: "post", data: p }))
//       ];

//       const totalPages = Math.ceil(allItems.length / pageSize);
//       const start = (page - 1) * pageSize;
//       const end = start + pageSize;

//       allItems.slice(start, end).forEach(item => {
//         if (item.type === "profile") renderProfile(item.data);
//         if (item.type === "post") renderPost(item.data);
//       });

//       for (let i = 1; i <= totalPages; i++) {
//         const btn = document.createElement("button");
//         btn.textContent = i;
//         btn.className = `
//           px-3 py-1 mx-1 rounded text-sm
//           ${i === page ? "bg-indigo-600 text-white" : "bg-gray-200"}
//         `;
//         btn.onclick = () => renderPage(i);
//         paginationContainer.appendChild(btn);
//       }
//     }

//     function renderProfile(p) {
//       const risk = p?.nlp?.risk || "low";

//       const card = document.createElement("div");
//       card.className = "bg-white p-4 rounded shadow";

//       card.innerHTML = `
//         <div class="flex justify-between items-center mb-2">
//           <span class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
//             ${p.platform}
//           </span>
//           <span class="text-xs px-2 py-1 rounded ${
//             risk === "high"
//               ? "bg-red-100 text-red-700"
//               : risk === "medium"
//               ? "bg-yellow-100 text-yellow-700"
//               : "bg-green-100 text-green-700"
//           }">
//             Risk: ${risk.toUpperCase()}
//           </span>
//         </div>

//         <h3 class="font-semibold">@${p.username || "unknown"}</h3>

//         <a href="${p.url}" target="_blank"
//            class="text-indigo-600 text-sm mt-2 inline-block">
//           View Profile →
//         </a>
//       `;

//       resultsContainer.appendChild(card);
//     }

//     function renderPost(post) {
//       const risk = post?.nlp?.risk || "unknown";

//       const card = document.createElement("div");
//       card.className = "bg-white p-4 rounded shadow";

//       card.innerHTML = `
//         <div class="text-xs text-gray-500 flex justify-between">
//           <span>${post.platform}</span>
//           <span>${post.date || ""}</span>
//         </div>

//         <p class="mt-2 text-sm text-gray-800">
//           ${post.text || "No content"}
//         </p>

//         <span class="inline-block mt-2 text-xs px-2 py-1 rounded ${
//           risk === "high"
//             ? "bg-red-100 text-red-700"
//             : risk === "medium"
//             ? "bg-yellow-100 text-yellow-700"
//             : "bg-gray-100 text-gray-700"
//         }">
//           NLP: ${risk.toUpperCase()}
//         </span>

//         <a href="${post.url}" target="_blank"
//            class="block text-indigo-600 text-sm mt-2">
//           View Post →
//         </a>
//       `;

//       resultsContainer.appendChild(card);
//     }

//     renderPage(currentPage);

//   } catch (err) {
//     resultsContainer.innerHTML = `
//       <div class="col-span-full text-red-600 text-center">
//         Error: ${err.message}
//       </div>
//     `;
//   }
// });

document.addEventListener("DOMContentLoaded", () => {

  let apiUrl = "api/x-posts";
  let nextUrl = null;
  let prevUrl = null;

  const postsContainer = document.getElementById("posts");
  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");

  async function fetchPosts(url) {
    try {
      const res = await fetch(url);
      const data = await res.json();

      nextUrl = data.next;
      prevUrl = data.previous;

      if (nextBtn) nextBtn.disabled = !nextUrl;
      if (prevBtn) prevBtn.disabled = !prevUrl;

      renderPosts(data.results);
    } catch (err) {
      console.error("Error fetching posts:", err);
      if (postsContainer) {
        postsContainer.innerHTML =
          `<p class="text-red-500">Failed to load posts.</p>`;
      }
    }
  }

  function renderPosts(posts) {
    if (!postsContainer) return;

    postsContainer.innerHTML = "";

    posts.forEach(post => {
      const postEl = document.createElement("div");
      postEl.className = "p-4 border rounded shadow-sm bg-gray-50";
      const textAnalysis =
              typeof post.text_analysis === "string"
            ? JSON.parse(post.text_analysis.replace(/'/g, '"'))
            : post.text_analysis;

    console.log(textAnalysis.sentiment);
    
    let sentiment = textAnalysis.sentiment;


      if (sentiment === "positive") {
        postEl.style.borderLeft = "4px solid green";
      } else if (sentiment === "negative") {
        postEl.style.borderLeft = "4px solid red";
      } else {
        postEl.style.borderLeft = "4px solid gray";
      }

      postEl.innerHTML = `
        <p class="text-sm text-gray-500">${new Date(post.date).toLocaleString()}</p>
        <h2 class="font-bold text-lg">@${post.username}</h2>
        <p class="mt-2">${post.text}</p>
        <p class="mt-2 text-gray-600 text-sm">
          Likes: ${post.like_count},
          Replies: ${post.reply_count},
          Retweets: ${post.retweet_count},
          Impressions: ${post.impression_count}
        </p>
        <p class="mt-2 text-gray-600 text-sm">
          NLP Risk: ${post.text_analysis || "unknown"}
        </p>
        <a href="${post.url}" target="_blank"
           class="text-blue-500 hover:underline text-sm">
          View on X
        </a>
      `;

      postsContainer.appendChild(postEl);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      if (nextUrl) fetchPosts(nextUrl);
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      if (prevUrl) fetchPosts(prevUrl);
    });
  }

  if (postsContainer) {
    fetchPosts(apiUrl);
  }

  // 👤 Profile dropdown
  const profileButton = document.getElementById("profileButton");
  const profileMenu = document.getElementById("profileMenu");

  if (profileButton && profileMenu) {
    profileButton.addEventListener("click", (e) => {
      e.stopPropagation();
      profileMenu.classList.toggle("hidden");
    });

    document.addEventListener("click", () => {
      profileMenu.classList.add("hidden");
    });
  }

});
