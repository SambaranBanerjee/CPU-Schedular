from typing import List, Dict, Tuple, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64

def sjf(processes: List[Dict[str, Any]]) -> Tuple[List[Tuple[str, float, float]], Dict[str, Any]]:
    # Defensive copy & normalize fields (pid -> str)
    proc_list = [
        {
            "pid": str(p.get("pid")),
            "arrival": float(p.get("arrival", 0)),
            "burst": float(p.get("burst", 0))
        }
        for p in processes
    ]
    proc_list.sort(key=lambda x: x["arrival"])

    n = len(proc_list)
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    burst = {p["pid"]: p["burst"] for p in proc_list}

    schedule: List[Tuple[str, float, float]] = []
    completion: Dict[str, float] = {}

    ready: List[Dict[str, Any]] = []
    time = 0.0
    i = 0

    if proc_list and proc_list[0]["arrival"] > 0:
        schedule.append(("IDLE", 0.0, proc_list[0]["arrival"]))
        time = proc_list[0]["arrival"]

    while len(completion) < n:
        while i < n and proc_list[i]["arrival"] <= time:
            ready.append(proc_list[i])
            i += 1

        if not ready:
            if i < n:
                next_arrival = proc_list[i]["arrival"]
                schedule.append(("IDLE", time, next_arrival))
                time = next_arrival
                continue
            else:
                break

        # Pick shortest job
        ready.sort(key=lambda x: x["burst"])
        p = ready.pop(0)

        start = float(time)
        end = start + float(p["burst"])
        schedule.append((p["pid"], start, end))
        time = end
        completion[p["pid"]] = end

    # Stats
    stats: Dict[str, Any] = {}
    total_tat = total_wt = 0.0

    for p in proc_list:
        pid = p["pid"]
        tat = float(completion.get(pid, 0.0) - arrival[pid])
        wt = float(tat - burst[pid])
        stats[pid] = {
            "arrival": arrival[pid],
            "burst": burst[pid],
            "completion": completion.get(pid, 0.0),
            "turnaround": tat,
            "waiting": wt
        }
        total_tat += tat
        total_wt += wt

    stats["avg_turnaround_time"] = float(total_tat / n) if n else 0.0
    stats["avg_waiting_time"] = float(total_wt / n) if n else 0.0

    return schedule, stats


def generate_sjf_gantt(schedule: List[Tuple[str, float, float]], title: str = "SJF Gantt Chart") -> str:
    pids: List[str] = []
    for pid, _, _ in schedule:
        if pid != "IDLE" and pid not in pids:
            pids.append(pid)
    if any(seg[0] == "IDLE" for seg in schedule):
        pids.append("IDLE")

    y_pos = {pid: idx for idx, pid in enumerate(reversed(pids))}
    cmap = plt.get_cmap("tab20")

    fig, ax = plt.subplots(figsize=(10, max(2, 2 + len(pids) * 0.3)))
    for idx, (pid, start, end) in enumerate(schedule):
        color = "#cccccc" if pid == "IDLE" else cmap(idx % 20)
        ax.barh(y=y_pos[pid], width=float(end - start), left=float(start), height=0.6, color=color, edgecolor="black")
        mid = (start + end) / 2
        if (end - start) >= 0.5:
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
