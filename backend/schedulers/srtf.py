def srtf(processes: List[Dict[str, Any]]) -> Tuple[List[Tuple[Any, float, float]], Dict[Any, Dict[str, float]]]:
    # Defensive copy and sort by arrival
    proc_list = [{"pid": p["pid"], "arrival": float(p["arrival"]), "burst": float(p["burst"])}
                 for p in processes]
    proc_list.sort(key=lambda x: x["arrival"])

    n = len(proc_list)
    arrival = {p["pid"]: p["arrival"] for p in proc_list}
    burst = {p["pid"]: p["burst"] for p in proc_list}
    rem = burst.copy()

    schedule = []              # (pid, start, end)
    completion = {}
    time = 0.0
    i = 0                     # next arrival index
    current_pid = None
    last_start_time = None

    ready = []                # list of (remaining_time, arrival_time, pid)

    import heapq
    heap = []                 # min-heap for SRTF

    # If first arrival > 0 → idle time
    if proc_list[0]["arrival"] > 0:
        schedule.append(("IDLE", 0, proc_list[0]["arrival"]))
        time = proc_list[0]["arrival"]

    while i < n or heap or current_pid:
        # Load new arrivals into heap
        while i < n and proc_list[i]["arrival"] <= time:
            p = proc_list[i]
            heapq.heappush(heap, (rem[p["pid"]], p["arrival"], p["pid"]))
            i += 1

        # If no process ready
        if not heap and current_pid is None:
            next_arrival = proc_list[i]["arrival"]
            schedule.append(("IDLE", time, next_arrival))
            time = next_arrival
            continue

        # Select process with min remaining time
        if current_pid is None:
            r, a, pid = heapq.heappop(heap)
            current_pid = pid
            last_start_time = time
        else:
            # Check if preemption is needed
            if heap and heap[0][0] < rem[current_pid]:
                # Preempt current
                schedule.append((current_pid, last_start_time, time))
                r, a, pid = heapq.heappop(heap)
                # push preempted process back
                heapq.heappush(heap, (rem[current_pid], arrival[current_pid], current_pid))
                current_pid = pid
                last_start_time = time

        # Determine next event time:
        # either process finishes OR new arrival comes
        next_finish = time + rem[current_pid]
        next_arrival = proc_list[i]["arrival"] if i < n else float("inf")
        next_event = min(next_finish, next_arrival)

        # Execute until next event
        exec_time = next_event - time
        rem[current_pid] -= exec_time
        time = next_event

        # If process completed
        if rem[current_pid] <= 0:
            schedule.append((current_pid, last_start_time, time))
            completion[current_pid] = time
            current_pid = None
            last_start_time = None

    # ---- Compute Stats ----
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
        "turnaround": total_tat / n if n else 0.0,
        "waiting": total_wt / n if n else 0.0
    }

    return schedule, stats
