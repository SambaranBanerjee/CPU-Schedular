from collections import deque
from typing import List, Dict, Tuple, Any
import random

#!/usr/bin/env python3

import matplotlib.pyplot as plt

def round_robin(processes: List[Dict[str, Any]], quantum: float) -> Tuple[List[Tuple[Any, float, float]], Dict[Any, Dict[str, float]]]:
    # Defensive copy and sort by arrival
    proc_list = [{"pid": p["pid"], "arrival": float(p["arrival"]), "burst": float(p["burst"])} for p in processes]
    proc_list.sort(key=lambda x: x["arrival"])
    n = len(proc_list)
    rem = {p["pid"]: p["burst"] for p in proc_list}
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    burst = {p["pid"]: p["burst"] for p in proc_list}

    schedule = []  # (pid, start, end)
    completion = {}
    q = deque()
    time = 0.0
    i = 0  # index for arrivals

    # Enqueue arrivals at time=0
    while i < n and proc_list[i]["arrival"] <= time:
        q.append(proc_list[i]["pid"])
        i += 1

    while q or i < n:
        if not q:
            # No ready process -> jump to next arrival (idle)
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

        # Enqueue any newly arrived processes by current time
        while i < n and proc_list[i]["arrival"] <= time:
            q.append(proc_list[i]["pid"])
            i += 1

        if rem[pid] > 0:
            q.append(pid)
        else:
            completion[pid] = time

    # Compute stats
    stats = {}
    total_wt = total_tat = 0.0
    for p in proc_list:
        pid = p["pid"]
        tat = completion[pid] - arrival[pid]
        wt = tat - burst[pid]
        stats[pid] = {"arrival": arrival[pid], "burst": burst[pid], "completion": completion[pid], "turnaround": tat, "waiting": wt}
        total_tat += tat
        total_wt += wt
    stats["average"] = {"turnaround": total_tat / n if n else 0.0, "waiting": total_wt / n if n else 0.0}
    return schedule, stats

def plot_gantt(schedule: List[Tuple[Any, float, float]], title: str = "Round Robin Gantt Chart") -> None:
    # Gather unique pids excluding IDLE and maintain order of first appearance
    pids = []
    for seg in schedule:
        pid = seg[0]
        if pid != "IDLE" and pid not in pids:
            pids.append(pid)
    # Add IDLE as last row if present
    has_idle = any(seg[0] == "IDLE" for seg in schedule)
    if has_idle:
        pids.append("IDLE")

    y_pos = {pid: idx for idx, pid in enumerate(reversed(pids))}  # reverse so first is top

    cmap = plt.get_cmap("tab20")
    color_map = {}
    for idx, pid in enumerate(pids):
        if pid == "IDLE":
            color_map[pid] = "#dddddd"
        else:
            color_map[pid] = cmap(idx % 20)

    fig, ax = plt.subplots(figsize=(10, max(2, len(pids) * 0.6)))
    for pid, start, end in schedule:
        ax.barh(y=y_pos[pid], width=end - start, left=start, height=0.6, color=color_map[pid], edgecolor="k")
        # label centered if wide enough
        mid = (start + end) / 2
        if end - start >= 0.5:
            ax.text(mid, y_pos[pid], str(pid), va="center", ha="center", color="black", fontsize=9)

    ax.set_yticks(list(y_pos.values()))
    ax.set_yticklabels(list(reversed(list(y_pos.keys()))))
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    def _get_float(prompt: str, default: float = None) -> float:
        while True:
            v = input(prompt).strip()
            if v == "" and default is not None:
                return float(default)
            try:
                return float(v)
            except ValueError:
                print("Please enter a numeric value.")

    def _get_int(prompt: str, default: int = None) -> int:
        while True:
            v = input(prompt).strip()
            if v == "" and default is not None:
                return int(default)
            try:
                return int(v)
            except ValueError:
                print("Please enter an integer value.")

    def get_processes_from_user() -> List[Dict[str, Any]]:
        processes = []
        print("Enter processes one at a time. Leave PID blank to finish.")
        i = 1
        while True:
            pid = input(f"PID for process #{i} (leave blank to finish): ").strip()
            if pid == "":
                if processes:
                    break
                else:
                    print("Please enter at least one process.")
                    continue

            arrival = _get_float(f"Arrival time for {pid} (default 0): ", default=0)
            while True:
                burst = input(f"Burst time for {pid}: ").strip()
                try:
                    burst_val = float(burst)
                    if burst_val <= 0:
                        print("Burst must be positive.")
                        continue
                    break
                except ValueError:
                    print("Please enter a numeric burst time.")

            processes.append({"pid": pid, "arrival": arrival, "burst": burst_val})
            i += 1

        return processes

    print("Round Robin scheduler — interactive mode")
    use_manual = input("Enter processes manually? (y/N): ").strip().lower() == "y"
    if use_manual:
        processes = get_processes_from_user()
        quantum = _get_float("Time quantum (e.g. 2): ")
    else:
        # Example fallback
        processes = [
            {"pid": "P1", "arrival": 0, "burst": 5},
            {"pid": "P2", "arrival": 1, "burst": 3},
            {"pid": "P3", "arrival": 2, "burst": 8},
            {"pid": "P4", "arrival": 3, "burst": 6},
        ]
        quantum = 2

    schedule, stats = round_robin(processes, quantum)

    print("\nGantt Schedule:")
    for seg in schedule:
        print(seg)
    print("\nPer-process stats:")
    for pid, s in stats.items():
        if pid == "average":
            continue
        print(f"{pid}: arrival={s['arrival']}, burst={s['burst']}, completion={s['completion']}, turnaround={s['turnaround']}, waiting={s['waiting']}")
    print("\nAverages:", stats["average"])

    try:
        plot_gantt(schedule, title=f"Round Robin (quantum={quantum})")
    except Exception as e:
        print("Unable to show chart:", e)
