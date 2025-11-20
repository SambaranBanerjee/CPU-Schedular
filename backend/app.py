from flask import Flask, request, jsonify
from flask_cors import CORS

from schedulers.rr import round_robin, generate_gantt_image
from schedulers.priority import priority_scheduling, generate_priority_gantt
from schedulers.fcfs import fcfs, generate_fcfs_gantt
from schedulers.sjf import sjf, generate_sjf_gantt
from schedulers.srtf import srtf, generate_srtf_gantt

app = Flask(__name__)
CORS(app) #This allows access for frontend

#This is the route for the initial path
@app.route("/")
def home():
    return jsonify({
        "status": "CPU Scheduling API running"
    })

#Now, these are path for schedules
@app.route("/schedule", methods=["POST"])
def schedule():
    try:
        data = request.get_json()

        algorithm = data.get("algorithm")
        processes = data.get("processes", [])
        
        #If not then:-
        if algorithm == "RR":
            quantum = float(data.get("quantum"))
            schedule, stats = round_robin(processes, quantum)
            image = generate_gantt_image(schedule, title=f"Round Robin (q={quantum})")
            
            return jsonify({
                "schedule": schedule,
                "stats": stats,
                "gantt_image": image
            })
        
        elif algorithm == "PRIORITY":
            schedule, stats = priority_scheduling(processes)
            image = generate_priority_gantt(schedule)

            return jsonify({
                "schedule": schedule,
                "stats": stats,
                "gantt_image": image
            })

        elif algorithm == "FCFS":
            schedule, stats = fcfs(processes)
            image = generate_fcfs_gantt(schedule)

            return jsonify({
                "schedule": schedule,
                "stats": stats,
                "gantt_image": image
            })
                
        elif algorithm == "SJF":
            schedule, stats = sjf(processes)
            image = generate_sjf_gantt(schedule)

            return jsonify({
                "schedule": schedule,
                "stats": stats,
                "gantt_image": image
            })
        
        elif algorithm == "SRTF":
            schedule, stats = srtf(processes)
            image = generate_srtf_gantt(schedule)

            return jsonify({
                "schedule": schedule,
                "stats": stats,
                "gantt_image": image
            })
        
        else:
            return jsonify({"error": f"Unknown algorithm '{algorithm}"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)