from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import traceback

# Add the project root to system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define the path to the frontend folder relative to this file
# api/index.py -> parent -> frontend
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

# Import schedulers
try:
    from schedulers.priority import priority_scheduling, generate_priority_gantt
    from schedulers.fcfs import fcfs, generate_fcfs_gantt
    from schedulers.rr import round_robin, generate_gantt_image
    from schedulers.sjf import sjf, generate_sjf_gantt
    from schedulers.srtf import srtf, generate_srtf_gantt
except ImportError as e:
    print(f"Import Error: {e}")

app = Flask(__name__)
CORS(app)

# --- Routes to Serve Frontend (Fallback) ---
@app.route('/')
def serve_frontend():
    # Serves the index.html file when / is requested
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    # Serves CSS, JS, and other static files
    return send_from_directory(FRONTEND_FOLDER, filename)

# --- API Routes ---
@app.route('/api')
@app.route('/api/')
def home():
    return jsonify({
        "status": "active", 
        "message": "Scheduler API is running."
    })

@app.route("/api/schedule", methods=["POST"])
def schedule():
    try:
        data = request.get_json()
        if not data:
             return jsonify({"error": "No JSON data received"}), 400

        algorithm = data.get("algorithm")
        processes = data.get("processes", [])
        
        schedule = []
        stats = {}
        image = ""

        if algorithm == "RR":
            quantum = float(data.get("quantum", 2))
            schedule, stats = round_robin(processes, quantum)
            image = generate_gantt_image(schedule, title=f"Round Robin (q={quantum})")
            
        elif algorithm == "PRIORITY":
            schedule, stats = priority_scheduling(processes)
            image = generate_priority_gantt(schedule)

        elif algorithm == "FCFS":
            schedule, stats = fcfs(processes)
            image = generate_fcfs_gantt(schedule)

        elif algorithm == "SJF":
            schedule, stats = sjf(processes)
            image = generate_sjf_gantt(schedule)
        
        elif algorithm == "SRTF":
            schedule, stats = srtf(processes)
            image = generate_srtf_gantt(schedule)
        
        else:
            return jsonify({"error": f"Unknown algorithm '{algorithm}'"}), 400

        return jsonify({
            "schedule": schedule,
            "stats": stats,
            "gantt_image": image
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500
    
if __name__ == "__main__":
    app.run(debug=True)