from collections import deque
from typing import List, Dict, Tuple, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64


def round_robin(processes: List[Dict[str, Any]], quantum: float):
    proc_list = [{"pid": p["pid"], "arrival": float(p["arrival"]), "burst": float(p["burst"])}
                 for p in processes]

    proc_list.sort(key=lambda x: x["arrival"])
    n = len(proc_list)

    rem = {p["pid"]: p["burst"] for p in proc_list}
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    burst = {p["pid"]: p["burst"] for p in proc_list}

    schedule = []
    completion = {}
    q = deque()
    time = 0.0
    i = 0

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
        start = time
        exec_time = min(quantum, rem[pid])
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

    stats = {}
    total_wt = total_tat = 0.0
    for p in proc_list:
        pid = p["pid"]
        tat = completion[pid] - arrival[pid]
        wt = tat - burst[pid]
        stats[pid] = {
            "arrival": arrival[pid],
            "burst": burst[pid],
            "completion": completion[pid],
            "turnaround": tat,
            "waiting": wt
        }
        total_tat += tat
        total_wt += wt

    stats["average"] = {
        "turnaround": total_tat / n if n else 0,
        "waiting": total_wt / n if n else 0,
    }

    return schedule, stats


def generate_gantt_image(schedule, title="Round Robin Gantt Chart"):
    pids = []
    for pid, _, _ in schedule:
        if pid != "IDLE" and pid not in pids:
            pids.append(pid)

    if any(seg[0] == "IDLE" for seg in schedule):
        pids.append("IDLE")

    y_pos = {pid: i for i, pid in enumerate(reversed(pids))}

    fig, ax = plt.subplots(figsize=(10, 2 + len(pids) * 0.3))
    cmap = plt.get_cmap("tab20")

    for idx, (pid, start, end) in enumerate(schedule):
        color = "#cccccc" if pid == "IDLE" else cmap(idx % 20)
        ax.barh(
            y=y_pos[pid],
            width=end - start,
            left=start,
            height=0.6,
            color=color,
            edgecolor="black"
        )
        mid = (start + end) / 2
        if end - start >= 0.4:
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
