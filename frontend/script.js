const processContainer = document.getElementById("process-container");
const addBtn = document.getElementById("add-process");

function addProcessRow() {
    const row = document.createElement("div");
    row.className = "process-row";
    row.innerHTML = `
        <div style="display:flex; gap:5px; align-items:center; width:100%;">
            <div><label>AT</label><input type="number" class="arrival" value="0"></div>
            <div><label>BT</label><input type="number" class="burst" value="5"></div>
            <div><label>Prio</label><input type="number" class="priority-input" value="1"></div>
            <div><label>Q</label><input type="number" class="quantum-input" value="2"></div>
            <button class="remove-btn" type="button">X</button>
        </div>
    `;
    row.querySelector(".remove-btn").onclick = () => row.remove();
    processContainer.appendChild(row);
}

addProcessRow();
addBtn.addEventListener("click", addProcessRow);

document.getElementById("schedule-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const rows = document.querySelectorAll(".process-row");
    const processes = [];
    rows.forEach((row, index) => {
        processes.push({
            pid: index + 1,
            arrival: parseFloat(row.querySelector(".arrival").value) || 0,
            burst: parseFloat(row.querySelector(".burst").value) || 0,
            priority: parseFloat(row.querySelector(".priority-input").value) || 0,
            quantum: parseFloat(row.querySelector(".quantum-input").value) || 2
        });
    });

    const payload = { processes: processes };

    try {
        const res = await fetch("/api/schedule", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        
        renderAllCharts(data);

    } catch (err) {
        console.error(err);
        alert("Failed to fetch data. Check backend console.");
    }
});


function renderAllCharts(data) {
    const grid = document.getElementById("charts-grid");
    const summaryBox = document.getElementById("comparison-summary");
    const bestAlgoSpan = document.getElementById("best-algo-name");

    grid.innerHTML = ""; 

    // Show Best Algorithm
    summaryBox.style.display = "block";
    bestAlgoSpan.textContent = data.best_algorithm;

    // Loop through results: FCFS, SJF, RR, etc.
    // data.results is an object { "FCFS": {...}, "RR": {...} }
    for (const [algoName, algoData] of Object.entries(data.results)) {
        
        const card = document.createElement("div");
        const isWinner = algoName === data.best_algorithm;
        
        card.className = `algo-card ${isWinner ? "winner" : ""}`;

        // Safe check for stats (handling 0 or undefined)
        const avgWait = algoData.stats.avg_waiting_time !== undefined 
                        ? algoData.stats.avg_waiting_time.toFixed(2) 
                        : "N/A";
        const avgTurn = algoData.stats.avg_turnaround_time !== undefined 
                        ? algoData.stats.avg_turnaround_time.toFixed(2) 
                        : "N/A";

        card.innerHTML = `
            <div class="algo-header">
                <span class="algo-title">${algoName}</span>
                ${isWinner ? '<span>⭐ Best Choice</span>' : ''}
            </div>
            
            <div class="stats-grid">
                <div><strong>Avg Waiting:</strong> ${avgWait}</div>
                <div><strong>Avg Turnaround:</strong> ${avgTurn}</div>
            </div>

            ${algoData.gantt_image 
                ? `<img src="data:image/png;base64,${algoData.gantt_image}" class="gantt-img" />` 
                : `<div style="padding:20px; text-align:center; background:#eee;">No Chart</div>`
            }
        `;

        grid.appendChild(card);
    }
}