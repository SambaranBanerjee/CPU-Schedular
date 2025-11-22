from typing import List, Dict, Tuple, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64

def fcfs(processes: List[Dict[str, Any]]) -> Tuple[List[Tuple[Any, float, float]], Dict[Any, Dict[str, float]]]:
    # Defensive copy & normalize fields
    proc_list = [{
        "pid": p["pid"],
        "arrival": float(p.get("arrival", 0)),
        "burst": float(p["burst"])
    } for p in processes]

    proc_list.sort(key=lambda x: x["arrival"])

    n = len(proc_list)
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    burst = {p["pid"]: p["burst"] for p in proc_list}

    schedule = []   # (pid, start, end)
    completion = {}

    time = 0.0
    stats = {}

    for p in proc_list:
        pid = p["pid"]
        at = arrival[pid]
        bt = burst[pid]

        if time < at:
            schedule.append(("IDLE", time, at))
            time = at

        start = time
        end = start + bt

        schedule.append((pid, start, end))
        completion[pid] = end
        time = end

    # Stats
    total_tat = total_wt = 0.0
    out_stats = {}

    for p in proc_list:
        pid = p["pid"]
        tat = completion[pid] - arrival[pid]
        wt = tat - burst[pid]
        out_stats[pid] = {
            "arrival": arrival[pid],
            "burst": burst[pid],
            "completion": completion[pid],
            "turnaround": tat,
            "waiting": wt
        }
        total_tat += tat
        total_wt += wt

    out_stats["average"] = {
        "turnaround": total_tat / n if n else 0.0,
        "waiting": total_wt / n if n else 0.0
    }

    return schedule, out_stats

def generate_fcfs_gantt(schedule, title="FCFS Gantt Chart"):
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