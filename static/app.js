

// Profile 
const profileButton = document.getElementById("profileButton");
const profileMenu = document.getElementById("profileMenu");

if (profileButton && profileMenu) {
  profileButton.addEventListener("click", (e) => {
    e.stopPropagation();
    profileMenu.classList.toggle("hidden");
  });

  document.addEventListener("click", (e) => {
    if (!profileButton.contains(e.target) && !profileMenu.contains(e.target)) {
      profileMenu.classList.add("hidden");
    }
  });
  }


const summaryUrl = "/api/narrative";  
const container = document.getElementById("cluster-container");

function getRiskColor(score) {
    if (score > 0.6) return "text-red-400";
    if (score > 0.3) return "text-yellow-400";
    return "text-green-400";
}

// Fetch cluster data from API
async function loadClusters() {
    try {
        const response = await fetch(summaryUrl);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const clusteringData = await response.json();

        clusteringData.clusters.forEach(cluster => {
            const riskColor = getRiskColor(cluster.coordinated_score);

            const clusterCard = document.createElement("div");
            clusterCard.className = "bg-black/50 p-6 rounded-xl";

            clusterCard.innerHTML = `
                <div class="flex justify-between items-center mb-4">
                    <div>
                        <h3 class="text-xl font-bold">Cluster #${cluster.cluster_id}</h3>
                        <p class="text-gray-400 text-sm">${cluster.num_tweets} Tweets</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm text-gray-400">Coordinated Score</p>
                        <p class="text-xl font-bold ${riskColor}">
                            ${cluster.coordinated_score}
                        </p>
                    </div>
                </div>

                <div class="space-y-2">
                    ${cluster.tweets.map(tweet => `
                        <div class="bg-gray-800 p-3 rounded text-sm text-gray-300">
                            ${tweet}
                        </div>
                    `).join("")}
                </div>
            `;

            container.appendChild(clusterCard);
        });
    } catch (error) {
        console.error("Failed to load clusters:", error);
        container.innerHTML = `<p class="text-red-400">Failed to load clusters.</p>`;
    }
}

loadClusters();


var postModal = document.getElementById('postModal');

postModal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget;

    // Update modal dynamically
    postModal.querySelector('#modal-username').textContent = button.getAttribute('data-username');
    postModal.querySelector('#modal-text').textContent = button.getAttribute('data-text');
    postModal.querySelector('#modal-url').href = button.getAttribute('data-url');
    postModal.querySelector('#modal-label').textContent = button.getAttribute('data-label');
    postModal.querySelector('#modal-risk').textContent = button.getAttribute('data-risk');
    postModal.querySelector('#modal-score').textContent = button.getAttribute('data-score');
    postModal.querySelector('#modal-sentiment').textContent = button.getAttribute('data-sentiment');
    postModal.querySelector('#modal-polarity').textContent = button.getAttribute('data-polarity');
    postModal.querySelector('#modal-date').textContent = new Date(button.getAttribute('data-date')).toLocaleString();
    postModal.querySelector('#modal-likes').textContent = button.getAttribute('data-likes');
    postModal.querySelector('#modal-retweets').textContent = button.getAttribute('data-retweets');
    postModal.querySelector('#modal-replies').textContent = button.getAttribute('data-replies');
    postModal.querySelector('#modal-quotes').textContent = button.getAttribute('data-quotes');
});

function getModalRiskClass(risk) {
    if (risk === "high") return "text-red-500";
    if (risk === "medium") return "text-yellow-400";
    return "text-green-400";
}

document.addEventListener('DOMContentLoaded', () => {
        document.addEventListener('show.bs.modal', async function (event) {
            const modal = event.target;
            const container = modal.querySelector('[data-url]');
            if (!container || container.dataset.loaded === "true") return;

            const url = container.dataset.url;
            if (!url) return;

            try {
                const res = await fetch(url);
                const data = await res.json();  // parse JSON
                const posts = data.results;

                // Build HTML dynamically
                container.innerHTML = posts.map(post => `
                <button type="button" class="w-full text-left" data-bs-toggle="modal" data-bs-target="#postModal"
                data-username="${post.username}" data-text="${post.text}" data-url="${post.url}"
                data-label="${post.text_analysis?.label ?? ''}" data-risk="${post.text_analysis?.risk ?? 'unknown'}" data-score="${post.text_analysis?.score ?? ''}"
                data-sentiment="${post.text_analysis?.sentiment ?? ''}" data-polarity="${post.text_analysis?.polarity ?? ''}" data-date="${post.date}"
                data-likes="${post.like_count}" data-retweets="${post.retweet_count}" data-replies="${post.reply_count}" data-quotes="${post.quote_count}">
                <div class="glass-card p-6 rounded-xl hover:bg-gray-800 transition">
                    <div class="flex text-sm justify-between py-1 font-semibold">
                        <p>${post.username}</p>
                        <p class="font-light text-sm">${post.date}</p>
                    </div>
                    <p class="text-gray-400 my-2">${post.text}</p>
                    <div class="flex justify-between text-sm text-gray-400">
                        <div class="space-x-4">
                            <span>Cluster...</span>
                            <a href="${post.url}" target="_blank" rel="noopener noreferrer" class="text-blue-300">View on X</a>
                        </div>
                        <span class="font-semibold ${getModalRiskClass(post.text_analysis?.risk ?? 'unknown')}">${post.text_analysis?.risk ?? 'unknown'}</span>
                    </div>
                </div>
            </button>
            `).join('');

                container.dataset.loaded = "true";
            } catch (err) {
                console.error("Failed to load posts:", err);
                container.innerHTML = '<p class="text-red-400 p-4">Failed to load posts.</p>';
            }
        });
    });

