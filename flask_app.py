from flask import Flask, render_template, jsonify, Response
from storage import init_db, save_run, list_runs, get_run, get_last_run
from tester.runner import run_all
import json, time

app = Flask(__name__)
init_db()

_last_run_time = 0
MIN_INTERVAL = 300  # 1 run max toutes les 5 minutes

@app.get("/")
def consignes():
    return render_template('consignes.html')

@app.get("/run")
def trigger_run():
    global _last_run_time
    elapsed = time.time() - _last_run_time
    if elapsed < MIN_INTERVAL:
        return jsonify({"error": f"Attendez encore {int(MIN_INTERVAL - elapsed)}s"}), 429
    _last_run_time = time.time()
    report = run_all()
    save_run(report)
    return jsonify(report)

@app.get("/dashboard")
def dashboard():
    runs = list_runs(limit=20)
    last = get_last_run()
    return render_template("dashboard.html", runs=runs, last=last)

@app.get("/health")
def health():
    last = get_last_run()
    if not last:
        return jsonify({"status": "no_run"}), 200
    s = last.get("summary", {})
    return jsonify({
        "status": "healthy" if s.get("availability", 0) >= 0.8 else "degraded",
        "api": last.get("api"),
        "last_run": last.get("timestamp"),
        "availability": s.get("availability"),
        "error_rate": s.get("error_rate"),
        "latency_ms_avg": s.get("latency_ms_avg"),
        "latency_ms_p95": s.get("latency_ms_p95"),
    })

@app.get("/export")
def export_json():
    runs = list_runs(limit=20)
    payload = json.dumps(runs, indent=2, ensure_ascii=False)
    return Response(payload, mimetype="application/json",
                    headers={"Content-Disposition": "attachment; filename=runs_export.json"})

@app.get("/run/<int:run_id>")
def run_detail(run_id):
    report = get_run(run_id)
    if not report:
        return jsonify({"error": f"Run {run_id} introuvable"}), 404
    return jsonify(report)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
