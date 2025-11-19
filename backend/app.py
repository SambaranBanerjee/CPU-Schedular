from flask import Flask, request, jsonify
from flask_cors import CORS

from schedulers.rr import round_robin
from schedulers.priority import priority_scheduling

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
        processes = data.get("processes")
        quantum = data.get("quantum", None)

        if not processes:
            return jsonify({"error" : "No process data provided"}), 400
        
        if algorithm == "RR":
            if quantum is None:
                return jsonify({"error": "Quantum missing for RR"}), 400
            schedule, stats = round_robin(processes, float(quantum))    
        
        elif algorithm == "PRIORITY":
            schedule, stats = priority_scheduling(processes)

        else:
            return jsonify({"error": f"Unknown algorithm '{algorithm}"}), 400
        
        return jsonify({
            "schedule": schedule,
            "stats": stats
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)