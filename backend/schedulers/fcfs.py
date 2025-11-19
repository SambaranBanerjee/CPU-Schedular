from typing import List, Dict, Tuple, Any

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
