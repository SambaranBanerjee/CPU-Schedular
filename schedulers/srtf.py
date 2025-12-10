from typing import List, Dict, Tuple, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64
import heapq

def srtf(processes: List[Dict[str, Any]]) -> Tuple[List[Tuple[str, float, float]], Dict[str, Any]]:
    proc_list = [
        {"pid": str(p.get("pid")), "arrival": float(p.get("arrival", 0)), "burst": float(p.get("burst", 0))}
        for p in processes
    ]
    proc_list.sort(key=lambda x: x["arrival"])

    n = len(proc_list)
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    burst = {p["pid"]: p["burst"] for p in proc_list}
    rem = {pid: burst[pid] for pid in burst}

    schedule: List[Tuple[str, float, float]] = []
    completion: Dict[str, float] = {}
    time = 0.0
    i = 0
    current_pid = None
    last_start_time = None
    heap: List[Tuple[float, float, str]] = []

    if proc_list and proc_list[0]["arrival"] > 0:
        schedule.append(("IDLE", 0.0, proc_list[0]["arrival"]))
        time = proc_list[0]["arrival"]

    while i < n or heap or current_pid:
        # push new arrivals
        while i < n and proc_list[i]["arrival"] <= time:
            p = proc_list[i]
            heapq.heappush(heap, (rem[p["pid"]], p["arrival"], p["pid"]))
            i += 1

        if not heap and current_pid is None:
            if i < n:
                next_arrival = proc_list[i]["arrival"]
                schedule.append(("IDLE", time, next_arrival))
                time = next_arrival
                continue
            else:
                break

        if current_pid is None:
            r, a, pid = heapq.heappop(heap)
            current_pid = pid
            last_start_time = time
        else:
            if heap and heap[0][0] < rem[current_pid]:
                # preempt
                schedule.append((current_pid, last_start_time, time))
                heapq.heappush(heap, (rem[current_pid], arrival[current_pid], current_pid))
                r, a, pid = heapq.heappop(heap)
                current_pid = pid
                last_start_time = time

        next_finish = time + rem[current_pid]
        next_arrival = proc_list[i]["arrival"] if i < n else float("inf")
        next_event = min(next_finish, next_arrival)

        exec_time = next_event - time
        rem[current_pid] -= exec_time
        time = next_event

        if rem[current_pid] <= 1e-12:
            # completed
            schedule.append((current_pid, last_start_time, time))
            completion[current_pid] = time
            current_pid = None
            last_start_time = None

    # stats
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


def generate_srtf_gantt(schedule: List[Tuple[str, float, float]], title: str = "SRTF Gantt Chart") -> str:
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
        if (end - start) >= 0.3:
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
