
document.addEventListener("DOMContentLoaded", () => {

  let apiUrl = "http://127.0.0.1:8000/api/x-posts";
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
