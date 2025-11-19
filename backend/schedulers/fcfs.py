# schedulers/fcfs.py

def fcfs(processes):
    """
    FCFS Scheduling Algorithm
    processes = [
        {"pid": "P1", "burst": 5, "arrival": 0},
        ...
    ]
    """

    
    for p in processes:
        if "arrival" not in p:
            p["arrival"] = 0

    
    processes = sorted(processes, key=lambda x: x["arrival"])

    current_time = 0
    schedule = []
    stats = []

    for p in processes:
        pid = p["pid"]
        burst = float(p["burst"])
        arrival = float(p["arrival"])

        
        start_time = max(current_time, arrival)
        completion_time = start_time + burst

        schedule.append({
            "pid": pid,
            "start": start_time,
            "end": completion_time
        })
        stats.append({
            "pid": pid,
            "arrival": arrival,
            "burst": burst,
            "completion": completion_time,
            "turnaround": completion_time - arrival,
            "waiting": start_time - arrival
        })

        current_time = completion_time

    return schedule, stats
