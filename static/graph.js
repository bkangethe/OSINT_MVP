let graphUrl = "/api/graph";

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie("csrftoken");

async function renderSummary(summary) {
    const summaryUrl = "/api/summary";

    try {
        const response = await fetch(summaryUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ text: summary }) 
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();

        document.getElementById("ai-summary-text").textContent = data.summary || "No summary available.";
    } catch (err) {
        console.error("Failed to fetch AI summary:", err);
        document.getElementById("ai-summary-text").textContent = "Error fetching summary.";
    }
}

async function loadGraph() {
    const loadingOverlay = document.getElementById("graph-loading");

    try {
        const response = await fetch(graphUrl);
        const Data = await response.json();

        const graphData = Data.graph;

        loadingOverlay.style.display = "none"; // Hide spinner
        initGraph(graphData);


        const aiSummary = Data.description || "No summary available.";
        // renderSummary(aiSummary);

    } catch (error) {
        loadingOverlay.innerHTML = "<p style='color:white'>Failed to load graph</p>";
        console.error(error);
    }
}

function initGraph(graphData) {
    const container = document.getElementById("graph");
    container.innerHTML = "";

    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select(container)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("background", "#0f172a"); // dark background

    // =============================
    // DEFINITIONS: Arrow & Glow
    // =============================
    const defs = svg.append("defs");

    // Arrow marker
    defs.append("marker")
        .attr("id", "arrow")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 28)
        .attr("refY", 0)
        .attr("markerWidth", 5)
        .attr("markerHeight", 5)
        .attr("orient", "auto")
        .append("path")
        .attr("fill", "#64748b")
        .attr("d", "M0,-5L10,0L0,5");

    // Soft glow
    const glow = defs.append("filter").attr("id", "softGlow");
    glow.append("feGaussianBlur").attr("stdDeviation", "6").attr("result", "blur");
    const merge = glow.append("feMerge");
    merge.append("feMergeNode").attr("in", "blur");
    merge.append("feMergeNode").attr("in", "SourceGraphic");

    // =============================
    // SCALES
    // =============================
    const sizeScale = d3.scaleLinear()
        .domain([0, d3.max(graphData.nodes, d => d.tweet_count)])
        .range([16, 38]);

    const polarity = graphData.global_stats?.average_sentiment?.polarity || 0;

    function sentimentColor(d) {
        if (polarity < -0.05) return "#ef4444";   // negative
        if (polarity > 0.1) return "#22c55e";     // positive
        return "#3b82f6";                         // neutral
    }

    const centralNode = graphData.network_metrics.central_nodes?.degree;

    // =============================
    // ZOOMABLE GROUP
    // =============================
    const zoomGroup = svg.append("g");

    const zoom = d3.zoom()
        .scaleExtent([0.3, 3])
        .on("zoom", (event) => {
            zoomGroup.attr("transform", event.transform);
        });

    svg.call(zoom);

    // =============================
    // FORCE SIMULATION
    // =============================
    const simulation = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.edges)
            .id(d => d.id)
            .distance(170)
            .strength(0.6))
        .force("charge", d3.forceManyBody().strength(-650))
        .force("center", d3.forceCenter(width / 2, height / 2));

    // =============================
    // LINKS
    // =============================
    const link = zoomGroup.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graphData.edges)
        .enter()
        .append("line")
        .attr("stroke", "#334155")
        .attr("stroke-width", d => 1.5 + d.weight)
        .attr("marker-end", "url(#arrow)")
        .attr("opacity", 0.7);

    // =============================
    // NODES
    // =============================
    const nodeGroup = zoomGroup.append("g").attr("class", "nodes");

    const node = nodeGroup.selectAll("circle")
        .data(graphData.nodes)
        .enter()
        .append("circle")
        .attr("r", d => sizeScale(d.tweet_count))
        .attr("fill", sentimentColor)
        .attr("stroke", d => d.id === centralNode ? "#161201" : "#1e293b")
        .attr("stroke-width", d => d.id === centralNode ? 3 : 1.5)
        .attr("filter", d => d.id === centralNode ? "url(#softGlow)" : null)
        .style("cursor", "pointer")
        .call(d3.drag()
            .on("start", (event, d) => {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on("drag", (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on("end", (event, d) => {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            })
        );

    // =============================
    // TOOLTIP
    // =============================
    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "graph-tooltip")
        .style("position", "absolute")
        .style("background", "rgba(15,23,42,0.95)")
        .style("color", "#e2e8f0")
        .style("padding", "12px 14px")
        .style("border-radius", "10px")
        .style("font-size", "13px")
        .style("box-shadow", "0 10px 25px rgba(0,0,0,0.4)")
        .style("backdrop-filter", "blur(8px)")
        .style("pointer-events", "none")
        .style("display", "none");

    node.on("mouseover", (event, d) => {
        node.transition().duration(200).attr("opacity", 0.3);
        link.transition().duration(200).attr("opacity", 0.1);

        node.filter(n =>
            n.id === d.id ||
            graphData.edges.some(e =>
                (e.source.id === d.id && e.target.id === n.id) ||
                (e.target.id === d.id && e.source.id === n.id)
            )
        ).transition().duration(200).attr("opacity", 1);

        link.filter(l => l.source.id === d.id || l.target.id === d.id)
            .transition().duration(200)
            .attr("opacity", 1)
            .attr("stroke", "#facc15");

        tooltip.style("display", "block")
            .html(`
                <strong>${d.id}</strong><br>
                Tweets: ${d.tweet_count}<br>
                Degree: ${graphData.network_metrics.degree[d.id] || 0}<br>
                Mentions: ${d.mentions?.join(", ") || "None"}<br>
                URLs: ${d.urls?.length || 0}<br>
                Sentiment: ${polarity.toFixed(2)}
            `);
    })
    .on("mousemove", (event) => {
        tooltip.style("top", (event.pageY + 18) + "px")
               .style("left", (event.pageX + 18) + "px");
    })
    .on("mouseout", () => {
        node.transition().duration(200).attr("opacity", 1);
        link.transition().duration(200)
            .attr("opacity", 0.7)
            .attr("stroke", "#334155");

        tooltip.style("display", "none");
    });

    // =============================
    // BURST RINGS
    // =============================
    if (graphData.clusters) {
        graphData.clusters.forEach(cluster => {
            if (cluster.emerging_burst && cluster.nodes) {
                cluster.nodes.forEach(nodeId => {
                    const targetNode = node.filter(d => d.id === nodeId);
                    targetNode.each(d => {
                        const ring = zoomGroup.append("circle")
                            .attr("cx", d.x)
                            .attr("cy", d.y)
                            .attr("r", 20)
                            .attr("stroke", "#f97316")
                            .attr("stroke-width", 2)
                            .attr("fill", "none")
                            .attr("opacity", 0.7);

                        ring.transition()
                            .duration(1500)
                            .attr("r", 60)
                            .attr("opacity", 0)
                            .remove();
                    });
                });
            }
        });
    }

    // =============================
    // LABELS
    // =============================
    const label = zoomGroup.append("g")
        .selectAll("text")
        .data(graphData.nodes)
        .enter()
        .append("text")
        .text(d => d.id)
        .attr("fill", "#cbd5e1")
        .attr("font-size", 12)
        .attr("text-anchor", "middle");

    // =============================
    // SIMULATION TICK
    // =============================
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        label
            .attr("x", d => d.x)
            .attr("y", d => d.y - 28);
    });

    // =============================
    // NETWORK METRICS PANEL
    // =============================
    const metrics = graphData.network_metrics;
    document.getElementById("network-metrics").innerHTML = `
        <div class="bg-black/50 p-6 rounded-xl">
            <p class="text-gray-400 text-sm">Network Density</p>
            <p class="text-2xl font-bold">${metrics.density.toFixed(3)}</p>
        </div>
        <div class="bg-black/50 p-6 rounded-xl">
            <p class="text-gray-400 text-sm">Average Degree</p>
            <p class="text-2xl font-bold">${metrics.average_degree.toFixed(2)}</p>
        </div>
        <div class="bg-black/50 p-6 rounded-xl">
            <p class="text-gray-400 text-sm">Most Central (Degree)</p>
            <p class="text-2xl font-bold text-blue-400">
                ${metrics.central_nodes.degree}
            </p>
        </div>
    `;
}
loadGraph();
