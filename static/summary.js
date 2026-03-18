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