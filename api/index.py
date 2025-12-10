from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FRONTEND_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'frontend'
)

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


# ---------- Safe Converter ----------
def safe_float(x, default=0.0):
    try:
        return float(x)
    except:
        return default


# ---------- Normalize stats ----------
def normalize_stats(stats_dict):
    clean = {}
    for k, v in stats_dict.items():
        # Force the key to be a string so 'jsonify' doesn't crash on sorting
        clean[str(k)] = safe_float(v) 
    return clean


# ---------- Serve Frontend ----------
@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


@app.route("/<path:filename>")
def serve_static_files(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)


@app.route("/api")
@app.route("/api/")
def home():
    return jsonify({
        "status": "active",
        "message": "Scheduler API is running."
    })


# ---------- MAIN SCHEDULING ENDPOINT ----------
@app.route("/api/schedule", methods=["POST"])
def schedule():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        processes = data.get("processes", [])
        quantum = safe_float(data.get("quantum", 2), default=2)

        results = {}

        # ---- FCFS ----
        fcfs_schedule, fcfs_stats = fcfs(processes)
        results["FCFS"] = {
            "schedule": fcfs_schedule,
            "stats": normalize_stats(fcfs_stats),
            "gantt_image": generate_fcfs_gantt(fcfs_schedule)
        }

        # ---- SJF ----
        sjf_schedule, sjf_stats = sjf(processes)
        results["SJF"] = {
            "schedule": sjf_schedule,
            "stats": normalize_stats(sjf_stats),
            "gantt_image": generate_sjf_gantt(sjf_schedule)
        }

        # ---- SRTF ----
        srtf_schedule, srtf_stats = srtf(processes)
        results["SRTF"] = {
            "schedule": srtf_schedule,
            "stats": normalize_stats(srtf_stats),
            "gantt_image": generate_srtf_gantt(srtf_schedule)
        }

        # ---- PRIORITY ----
        pr_schedule, pr_stats = priority_scheduling(processes)
        results["PRIORITY"] = {
            "schedule": pr_schedule,
            "stats": normalize_stats(pr_stats),
            "gantt_image": generate_priority_gantt(pr_schedule)
        }

        # ---- ROUND ROBIN ----
        rr_schedule, rr_stats = round_robin(processes, quantum)
        results["RR"] = {
            "schedule": rr_schedule,
            "stats": normalize_stats(rr_stats),
            "gantt_image": generate_gantt_image(rr_schedule, title=f"RR (q={quantum})")
        }

        # ---- BEST ALGORITHM ----
        best = min(
            results.keys(),
            key=lambda algo: results[algo]["stats"].get("avg_waiting_time", float("inf"))
        )

        return jsonify({
            "results": results,
            "best_algorithm": best
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
