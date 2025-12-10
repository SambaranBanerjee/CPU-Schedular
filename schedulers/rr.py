from collections import deque
from typing import List, Dict, Tuple, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64

def round_robin(processes: List[Dict[str, Any]], quantum: float) -> Tuple[List[Tuple[str, float, float]], Dict[str, Any]]:
    proc_list = [
        {"pid": str(p.get("pid")), "arrival": float(p.get("arrival", 0)), "burst": float(p.get("burst", 0))}
        for p in processes
    ]
    proc_list.sort(key=lambda x: x["arrival"])
    n = len(proc_list)

    rem = {p["pid"]: p["burst"] for p in proc_list}
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    burst = {p["pid"]: p["burst"] for p in proc_list}

    schedule: List[Tuple[str, float, float]] = []
    completion: Dict[str, float] = {}
    q = deque()
    time = 0.0
    i = 0

    # enqueue initial arrivals
    while i < n and proc_list[i]["arrival"] <= time:
        q.append(proc_list[i]["pid"])
        i += 1

    while q or i < n:
        if not q:
            next_arrival = proc_list[i]["arrival"]
            schedule.append(("IDLE", time, next_arrival))
            time = next_arrival
            while i < n and proc_list[i]["arrival"] <= time:
                q.append(proc_list[i]["pid"])
                i += 1
            continue

        pid = q.popleft()
        start = float(time)
        exec_time = min(float(quantum), rem[pid])
        end = start + exec_time
        schedule.append((pid, start, end))
        rem[pid] -= exec_time
        time = end

        while i < n and proc_list[i]["arrival"] <= time:
            q.append(proc_list[i]["pid"])
            i += 1

        if rem[pid] > 0:
            q.append(pid)
        else:
            completion[pid] = time

    stats: Dict[str, Any] = {}
    total_tat = total_wt = 0.0
    for p in proc_list:
        pid = p["pid"]
        comp = completion.get(pid, 0.0)
        tat = float(comp - arrival[pid])
        wt = float(tat - burst[pid])
        stats[pid] = {
            "arrival": arrival[pid],
            "burst": burst[pid],
            "completion": comp,
            "turnaround": tat,
            "waiting": wt
        }
        total_tat += tat
        total_wt += wt

    stats["avg_turnaround_time"] = float(total_tat / n) if n else 0.0
    stats["avg_waiting_time"] = float(total_wt / n) if n else 0.0

    return schedule, stats

def generate_gantt_image(schedule: List[Tuple[str, float, float]], title: str = "Round Robin Gantt Chart") -> str:
    pids: List[str] = []
    for pid, _, _ in schedule:
        if pid != "IDLE" and pid not in pids:
            pids.append(pid)
    if any(seg[0] == "IDLE" for seg in schedule):
        pids.append("IDLE")

    y_pos = {pid: i for i, pid in enumerate(reversed(pids))}
    cmap = plt.get_cmap("tab20")

    fig, ax = plt.subplots(figsize=(10, max(2, 2 + len(pids) * 0.3)))
    for idx, (pid, start, end) in enumerate(schedule):
        color = "#cccccc" if pid == "IDLE" else cmap(idx % 20)
        ax.barh(y=y_pos[pid], width=float(end - start), left=float(start), height=0.6, color=color, edgecolor="black")
        mid = (start + end) / 2
        if (end - start) >= 0.4:
            ax.text(mid, y_pos[pid], pid, ha="center", va="center", fontsize=8)

    ax.set_yticks(list(y_pos.values()))
    ax.set_yticklabels(list(reversed(pids)))
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.grid(axis="x", linestyle="--", alpha=0.3)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
