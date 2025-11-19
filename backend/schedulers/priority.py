from typing import List, Dict, Tuple, Any
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
