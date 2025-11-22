from typing import List, Dict, Tuple, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64

def sjf(processes: List[Dict[str, Any]]) -> Tuple[List[Tuple[Any, float, float]], Dict[Any, Dict[str, float]]]:
    # Defensive copy and sort by arrival
    proc_list = [{"pid": p["pid"], "arrival": float(p["arrival"]), "burst": float(p["burst"])} for p in processes]
    proc_list.sort(key=lambda x: x["arrival"])

    n = len(proc_list)
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    burst = {p["pid"]: p["burst"] for p in proc_list}

    schedule = []  # (pid, start, end)
    completion = {}

    ready = []
    time = 0.0
    i = 0  # index for arrivals

    # Initial step: if first arrival > 0, idle till then
    if proc_list and proc_list[0]["arrival"] > 0:
        schedule.append(("IDLE", 0.0, proc_list[0]["arrival"]))
        time = proc_list[0]["arrival"]

    while len(completion) < n:
        # Add all arrivals up to current time
        while i < n and proc_list[i]["arrival"] <= time:
            ready.append(proc_list[i])
            i += 1

        if not ready:
            # No ready process → go to next arrival
            next_arrival = proc_list[i]["arrival"]
            schedule.append(("IDLE", time, next_arrival))
            time = next_arrival
            continue

        # Pick shortest job
        ready.sort(key=lambda x: x["burst"])
        p = ready.pop(0)

        start = time
        end = start + p["burst"]
        schedule.append((p["pid"], start, end))
        time = end
        completion[p["pid"]] = end

    # Compute stats
    stats = {}
    total_tat = total_wt = 0.0

    for p in proc_list:
        pid = p["pid"]
        tat = completion[pid] - arrival[pid]
        wt = tat - burst[pid]
        stats[pid] = {
            "arrival": arrival[pid],
            "burst": burst[pid],
            "completion": completion[pid],
            "turnaround": tat,
            "waiting": wt,
        }
        total_tat += tat
        total_wt += wt

    stats["average"] = {
        "turnaround": total_tat / n,
        "waiting": total_wt / n,
    }

    return schedule, stats


def generate_sjf_gantt(schedule, title="SJF Gantt Chart"):
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