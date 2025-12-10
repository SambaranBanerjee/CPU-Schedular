from typing import List, Dict, Tuple, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64

def priority_scheduling(processes: List[Dict[str, Any]]) -> Tuple[List[Tuple[str, float, float]], Dict[str, Any]]:

    # Normalize input: pid as str, others as float
    proc_list = [
        {
            "pid": str(p["pid"]),
            "arrival": float(p["arrival"]),
            "burst": float(p["burst"]),
            "priority": float(p["priority"])
        }
        for p in processes
    ]

    # Sort by arrival to help with initial checks
    proc_list.sort(key=lambda x: x["arrival"])

    n = len(proc_list)
    
    # Static info for stats calculation later
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    original_burst = {p["pid"]: p["burst"] for p in proc_list}
    priority = {p["pid"]: p["priority"] for p in proc_list}

    # Dynamic tracking
    remaining_time = {p["pid"]: p["burst"] for p in proc_list}
    
    schedule: List[Tuple[str, float, float]] = []
    completion: Dict[str, float] = {}

    current_time = 0.0
    completed_count = 0
    
    # We simulate time step by step (1 unit at a time) to allow preemption
    # For floating point bursts, this logic assumes 1.0 steps. 
    # If you need sub-integer precision, the step logic becomes more complex (event-driven).
    
    while completed_count < n:
        # 1. Find all processes that have arrived and are not finished
        ready_queue = [
            p for p in proc_list 
            if p["arrival"] <= current_time and remaining_time[p["pid"]] > 0
        ]

        if not ready_queue:
            # CPU is Idle
            # Optimization: Jump to the next arrival time to save loop iterations
            future_arrivals = [p["arrival"] for p in proc_list if p["arrival"] > current_time]
            if future_arrivals:
                next_event = min(future_arrivals)
                # Record IDLE block
                schedule.append(("IDLE", current_time, next_event))
                current_time = next_event
            else:
                # Should not happen if completed_count < n, but safety break
                break
            continue

        # 2. Select process with highest priority (Lowest Number = Highest Priority)
        # Tie-breaker: If priorities are equal, usually FCFS is used (Python's min is stable for lists)
        current_proc = min(ready_queue, key=lambda x: x["priority"])
        pid = current_proc["pid"]

        # 3. Execute for 1 time unit
        start_t = current_time
        end_t = current_time + 1.0
        
        remaining_time[pid] -= 1.0
        current_time += 1.0

        # 4. Check if finished
        if remaining_time[pid] <= 0:
            # Determine exact finish time in case burst was less than 1.0 (float handling)
            diff = abs(remaining_time[pid]) 
            end_t -= diff # Adjust end time if we overshot (e.g. burst was 0.5)
            current_time -= diff # Correct global time
            remaining_time[pid] = 0 # Clean up
            
            completed_count += 1
            completion[pid] = current_time

        # 5. Add to Schedule (Visual Optimization)
        # If the last entry in schedule is the same PID, extend it instead of creating a new entry.
        # This prevents the Gantt chart from looking like a "barcode".
        if schedule and schedule[-1][0] == pid and abs(schedule[-1][2] - start_t) < 0.001:
            # Update the 'end' time of the last tuple
            last_pid, last_start, _ = schedule[-1]
            schedule[-1] = (last_pid, last_start, end_t)
        else:
            schedule.append((pid, start_t, end_t))


    # --- Stats Calculation (Same as before) ---
    stats: Dict[str, Any] = {}
    total_tat = 0.0
    total_wt = 0.0

    for p in proc_list:
        pid = p["pid"]
        tat = float(completion[pid] - arrival[pid])
        wt = float(tat - original_burst[pid]) # WT = TAT - Burst

        stats[pid] = {
            "arrival": arrival[pid],
            "burst": original_burst[pid],
            "priority": priority[pid],
            "completion": completion[pid],
            "turnaround": tat,
            "waiting": wt
        }

        total_tat += tat
        total_wt += wt

    stats["avg_turnaround_time"] = float(total_tat / n) if n else 0.0
    stats["avg_waiting_time"] = float(total_wt / n) if n else 0.0

    return schedule, stats


def generate_priority_gantt(schedule: List[Tuple[str, float, float]], title="Preemptive Priority Gantt Chart") -> str:
    # (This function remains exactly the same as your provided code)
    pids = []
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

        ax.barh(
            y=y_pos[pid],
            width=float(end - start),
            left=float(start),
            height=0.6,
            color=color,
            edgecolor="black"
        )

        mid = (start + end) / 2
        if (end - start) >= 0.5:
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