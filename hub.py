import os
import sys
import re
import io
import time
import threading
import webbrowser
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from pyngrok import ngrok

app = Flask(__name__)

# --- IN-MEMORY STATE ---
active_agents = {}
active_session = {
    "is_active": False,
    "name": "",
    "form_link": "",
    "public_url": "",
    "students": [],
    "logs": []
}

# --- HOST TAB WATCHDOG ---
last_host_ping = time.time()
dashboard_opened = False

def host_watchdog():
    """Terminates Python and ngrok if the professor closes the dashboard browser tab."""
    global last_host_ping, dashboard_opened
    while True:
        time.sleep(2)
        if dashboard_opened and (time.time() - last_host_ping > 7):
            print("\n[*] Professor dashboard tab closed. Shutting down ProctorHub...")
            try:
                ngrok.kill()
            except Exception:
                pass
            os._exit(0)

threading.Thread(target=host_watchdog, daemon=True).start()

# --- HOST HEARTBEAT ROUTES ---
@app.route('/api/host_ping', methods=['POST'])
def host_ping():
    global last_host_ping, dashboard_opened
    dashboard_opened = True
    last_host_ping = time.time()
    return jsonify({"status": "ok"})

@app.route('/api/host_shutdown', methods=['POST'])
def host_shutdown():
    print("\n[*] Direct shutdown signal received from host tab. Exiting...")
    try:
        ngrok.kill()
    except Exception:
        pass
    os._exit(0)

# --- PORTAL & DASHBOARD PAGES ---
@app.route('/')
def professor_dashboard():
    return render_template('index.html', session=active_session)

@app.route('/student')
def student_portal():
    return render_template(
        'student.html',
        session_active=active_session["is_active"],
        session_name=active_session["name"],
        session_url=active_session["public_url"],
        form_link=active_session["form_link"]
    )

# --- SESSION LIFECYCLE ---
@app.route('/api/create_session', methods=['POST'])
def create_session():
    data = request.json or {}
    active_session['name'] = data.get('session_name', 'Exam').strip()
    active_session['form_link'] = data.get('form_link', '').strip()
    active_session['is_active'] = True
    active_session['students'] = []
    active_session['logs'] = []
    active_agents.clear()

    if not active_session['public_url']:
        tunnel = ngrok.connect(5000)
        active_session['public_url'] = tunnel.public_url
        print(f"[*] Live Tunnel: {active_session['public_url']}")

    return jsonify({"status": "success", "public_url": active_session['public_url']})

@app.route('/download/agent')
def download_agent():
    master_path = os.path.join(app.root_path, 'static', 'MasterAgent.exe')
    if not os.path.exists(master_path):
        return "MasterAgent.exe missing from static folder. Please compile it first.", 404

    clean_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', active_session['name'])
    clean_filename = f"ProctoredExam_{clean_title}.exe"
    return send_file(master_path, as_attachment=True, download_name=clean_filename)

# --- AGENT AUTO-HANDSHAKE & HEARTBEAT ---
@app.route('/api/agent_checkin', methods=['POST'])
def agent_checkin():
    token = request.json.get("token", "").strip() if request.json else ""
    if not token or not active_session['is_active']:
        return jsonify({"status": "error"}), 400

    if token not in active_agents:
        active_agents[token] = {
            "status": "waiting",
            "student_id": None,
            "last_seen": time.time(),
            "closed_flagged": False
        }
    else:
        active_agents[token]["last_seen"] = time.time()

    return jsonify({"status": "success"})

@app.route('/api/check_agent_live', methods=['GET'])
def check_agent_live():
    token = request.args.get("token", "").strip()
    agent = active_agents.get(token)
    is_live = agent is not None and (time.time() - agent["last_seen"] < 8)
    return jsonify({"is_live": is_live})

@app.route('/api/start_exam', methods=['POST'])
def start_exam():
    data = request.json or {}
    name = data.get("name", "").strip()
    sid = data.get("student_id", "").strip()
    email = data.get("email", "").strip()
    token = data.get("token", "").strip()

    if not name or not sid or not token:
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    if token not in active_agents:
        return jsonify({"status": "error", "message": "Proctor agent not detected on this machine."}), 400

    active_agents[token]["status"] = "active"
    active_agents[token]["student_id"] = sid

    existing = next((s for s in active_session['students'] if s['student_id'] == sid), None)
    if not existing:
        active_session['students'].append({
            "name": name,
            "student_id": sid,
            "email": email,
            "token": token,
            "status": "in_progress"
        })
    else:
        existing["status"] = "in_progress"
        existing["token"] = token

    return jsonify({"status": "success", "form_link": active_session['form_link']})

@app.route('/api/agent_heartbeat', methods=['POST'])
def agent_heartbeat():
    data = request.json or {}
    token = data.get("token", "").strip()

    if token in active_agents:
        active_agents[token]["last_seen"] = time.time()
        return jsonify({
            "status": active_agents[token]["status"],
            "student_id": active_agents[token]["student_id"],
            "session_active": active_session['is_active']
        })
    return jsonify({"status": "unknown"})

@app.route('/api/finish_student', methods=['POST'])
def finish_student():
    sid = request.json.get('student_id', '').strip() if request.json else ""
    for s in active_session['students']:
        if s['student_id'] == sid:
            s['status'] = 'completed'
            token = s.get('token')
            if token and token in active_agents:
                active_agents[token]["status"] = "completed"
            return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Student not found."}), 404

# --- VIOLATION LOGGING & MONITORING ---
@app.route('/log', methods=['POST'])
def log_violation():
    data = request.json or {}
    sid = data.get('student_id')
    student = next((s for s in active_session['students'] if s['student_id'] == sid), None)
    if student and student.get('status') == 'completed':
        return jsonify({"status": "ignored"}), 200

    active_session['logs'].append(data)
    return jsonify({"status": "success"}), 200

@app.route('/api/live_data', methods=['GET'])
def live_data():
    if not active_session['is_active']:
        return jsonify([])

    current_t = time.time()
    for token, info in active_agents.items():
        if info["status"] == "active" and not info["closed_flagged"]:
            if (current_t - info["last_seen"]) > 6:
                info["closed_flagged"] = True
                sid = info["student_id"]
                if sid:
                    active_session['logs'].append({
                        "student_id": sid,
                        "category": "Agent Terminated",
                        "details": "[CRITICAL] Proctor agent was closed or process terminated during exam",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })

    rows = []
    for s in active_session['students']:
        s_logs = [l for l in active_session['logs'] if l.get('student_id') == s['student_id']]
        rows.append({
            "name": s['name'],
            "student_id": s['student_id'],
            "status": s.get('status', 'in_progress'),
            "violations": len(s_logs),
            "details": " | ".join(set([l['details'] for l in s_logs])) if s_logs else "None"
        })
    return jsonify(rows)

@app.route('/api/end_session', methods=['POST'])
def end_session():
    active_session['is_active'] = False
    report = []
    for s in active_session['students']:
        s_logs = [l for l in active_session['logs'] if l.get('student_id') == s['student_id']]
        report.append({
            "Student Name": s['name'],
            "Student ID": s['student_id'],
            "Email": s['email'],
            "Status": s.get('status', 'completed').title(),
            "Total Violations": len(s_logs),
            "Violation Details": "\n".join([f"[{l.get('timestamp', '')}] {l['details']}" for l in s_logs]) if s_logs else "Clean"
        })

    df = pd.DataFrame(report) if report else pd.DataFrame(columns=["Student Name", "Student ID", "Email", "Status", "Total Violations", "Violation Details"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Exam Report")
    output.seek(0)

    if active_session['public_url']:
        ngrok.kill()
        active_session['public_url'] = ""

    filename = f"Exam_Report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:5000')).start()
    app.run(port=5000, use_reloader=False)