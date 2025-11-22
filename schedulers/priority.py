from typing import List, Dict, Tuple, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64
#The processes are in a list of Dictionary labelled by process name (string) and value (type = any)
def priority_scheduling(processes: List[Dict[str, Any]]) -> Tuple[List[Tuple[Any, float, float]], Dict[Any, Dict[str, float]]]:
    
    proc_list = [
        {
            "pid": p["pid"], 
            "arrival": float(p["arrival"]), 
            "burst": float(p["burst"]), 
            "priority": float(p["priority"])
        }
        for p in processes
    ]
    #I sort the process list on the basis of arrival time
    proc_list.sort(key=lambda x: x["arrival"])

    n = len(proc_list)
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    burst = {p["pid"]: p["burst"] for p in proc_list}
    priority = {p["pid"]: p["priority"] for p in proc_list}

    schedule = []
    completion = {}

    time = 0.0
    finished = set()
    completed_count = 0

    while completed_count < n:
        # This collects all arrived & not finished processes
        ready = [
            p for p in proc_list
            if p["arrival"] <= time and p["pid"] not in finished
        ]

        if not ready:
            # Now I am adding a condition that if CPU is idle then jump to next arrival
            next_arrival = min(
                [p["arrival"] for p in proc_list if p["pid"] not in finished]
            )
            schedule.append(("IDLE", time, next_arrival))
            time = next_arrival
            continue

        #I select highest priority (lowest priority value wins)
        current = min(ready, key=lambda x: x["priority"])
        pid = current["pid"]

        start = time
        end = start + burst[pid]

        # Now I execute the schedule
        schedule.append((pid, start, end))

        completion[pid] = end
        finished.add(pid)
        completed_count += 1
        time = end

    stats = {}
    total_tat = total_wt = 0.0

    for p in proc_list:
        pid = p["pid"]
        tat = completion[pid] - arrival[pid]    #Turnaround time
        wt = tat - burst[pid]   #Waiting time
        stats[pid] = {
            "arrival": arrival[pid],
            "burst": burst[pid],
            "priority": priority[pid],
            "completion": completion[pid],
            "turnaround": tat,
            "waiting": wt,
        }
        total_tat += tat
        total_wt += wt

    stats["average"] = {
        "turnaround": total_tat / n if n else 0.0,
        "waiting": total_wt / n if n else 0.0,
    }

    return schedule, stats

def generate_priority_gantt(schedule, title="Priority Scheduling Gantt Chart"):
    pids = []
    for pid, _, _ in schedule:
        if pid != "IDLE" and pid not in pids:
            pids.append(pid)
    if any(seg[0] == "IDLE" for seg in schedule):
        pids.append("IDLE")

    y_pos = {pid: idx for idx, pid in enumerate(reversed(pids))}

    cmap = plt.get_cmap("tab20")

    fig, ax = plt.subplots(figsize=(10, 2 + len(pids) * 0.3))
    for idx, (pid, start, end) in enumerate(schedule):
        color = "#cccccc" if pid == "IDLE" else cmap(idx % 20)
        ax.barh(
            y=y_pos[pid],
            width=end - start,
            left=start,
            height=0.6,
            color=color,
            edgecolor="black",
        )

        mid = (start + end) / 2
        if end - start >= 0.5:
            ax.text(mid, y_pos[pid], pid, ha="center", va="center", fontsize=8)

    ax.set_yticks(list(y_pos.values()))
    ax.set_yticklabels(list(reversed(pids)))
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.grid(axis="x", linestyle="--", alpha=0.3)

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")