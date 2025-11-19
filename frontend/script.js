let selectedAlgo = "RR";
const algoButtons = document.querySelectorAll(".algo-btn");
const formTitle = document.getElementById("form-title");
const quantumField = document.getElementById("quantum-field");
const processContainer = document.getElementById("process-container");
const addProcessBtn = document.getElementById("add-process");
const form = document.getElementById("schedule-form");
const ganttChart = document.getElementById("gantt-chart");

algoButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        algoButtons.forEach(b => b.classList.remove("algo-active"));
        btn.classList.add("algo-active");
        selectedAlgo = btn.dataset.type;
        formTitle.textContent = `${selectedAlgo} Parameters`;
        quantumField.style.display = selectedAlgo === "RR" ? "block" : "none";
    });
});
function fcfs(processes) {

    /* --- FIXED: id → pid (your input uses pid) --- */
    processes.forEach(p => {
        if (!p.pid) p.pid = p.id;
    });

    let currentTime = 0;
    let result = [];
    let gantt = [];

    /* --- FIXED: sort by arrival time --- */
    processes.sort((a, b) => a.arrival - b.arrival);

    processes.forEach(p => {
        if (currentTime < p.arrival) currentTime = p.arrival;

        let start = currentTime;
        let finish = start + p.burst;

        result.push({
            pid: p.pid,
            burst: p.burst,
            start: start,
            completion: finish,
            turnaround: finish - p.arrival, /* --- FIXED --- */
            waiting: start - p.arrival      /* --- FIXED --- */
        });

        gantt.push({
            pid: p.pid,
            start: start,
            end: finish
        });

        currentTime = finish;
    });

    return { table: result, gantt: gantt };
}


function addProcessRow() {
    const row = document.createElement("div");
    row.classList.add("process-row");
    row.innerHTML = `
        <input class="small-input" placeholder="PID">
        <input class="small-input" type="number" placeholder="Arrival">
        <input class="small-input" type="number" placeholder="Burst">
        ${selectedAlgo === "PRIORITY" ? `<input class="priority-input" type="number" placeholder="Priority">` : ""}
        <button type="button" onclick="this.parentElement.remove()">X</button>
    `;
    processContainer.appendChild(row);
}

addProcessBtn.addEventListener("click", addProcessRow);
addProcessRow();

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const processes = [];
    document.querySelectorAll(".process-row").forEach(row => {
        const inputs = row.querySelectorAll("input");
        const [pid, at, bt] = inputs;
        const pr = inputs[3];

        if (pid.value && at.value && bt.value) {
            const p = {
                pid: pid.value,
                arrival: Number(at.value),
                burst: Number(bt.value)
            };
            if (selectedAlgo === "PRIORITY" && pr?.value) p.priority = Number(pr.value);
            processes.push(p);
        }
    });

    const body = { algorithm: selectedAlgo, processes };
    if (selectedAlgo === "RR") body.quantum = Number(document.getElementById("quantum").value);

    const res = await fetch("http://127.0.0.1:5000/schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    const data = await res.json();
    renderGantt(data.schedule);
});

function renderGantt(schedule) {
    ganttChart.innerHTML = "";
    if (!schedule) return;

    schedule.forEach(seg => {
        const block = document.createElement("div");
        block.style.display = "inline-block";
        block.style.padding = "10px";
        block.style.marginRight = "4px";
        block.style.background = "#3f51b5";
        block.style.borderRadius = "4px";
        block.textContent = `${seg.pid} (${seg.start}-${seg.end})`;
        ganttChart.appendChild(block);
    });
}
