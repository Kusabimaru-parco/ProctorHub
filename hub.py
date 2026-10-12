import os
import sys
import re
import io
import time
import json
import threading
import webbrowser
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from pyngrok import ngrok, conf

app = Flask(__name__)

# --- STATE PERSISTENCE ---
STATE_FILE = "proctor_state.json"

server_globals = {
    "ngrok_running": False
}

active_agents = {}
active_session = {
    "is_active": False,
    "name": "",
    "form_link": "",
    "public_url": "",
    "students": [],
    "logs": []
}

def save_state():
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({
                "session": active_session,
                "agents": active_agents
            }, f)
    except Exception as e:
        print(f"[!] Error saving state: {e}")

def load_state():
    global active_session, active_agents
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                active_session.update(data.get("session", {}))
                active_agents.update(data.get("agents", {}))
                print("[*] Previous session state loaded successfully.")
        except Exception:
            pass

load_state()

# --- MANUAL SERVER SHUTDOWN ---
@app.route('/api/shutdown_server', methods=['POST'])
def shutdown_server():
    print("\n[*] Server shutdown initiated by professor. Exiting...")
    try:
        ngrok.kill()
    except Exception:
        pass
    os._exit(0)

# --- PORTAL & SETUP PAGES ---
@app.route('/')
def index_router():
    if not server_globals["ngrok_running"]:
        return render_template('setup.html')
    return render_template('index.html', session=active_session)

@app.route('/api/init_server', methods=['POST'])
def init_server():
    token = request.json.get('token', '').strip()
    domain = request.json.get('domain', '').strip()

    if not token:
        return jsonify({"status": "error", "message": "Auth token is required."}), 400

    try:
        ngrok.set_auth_token(token)
        if domain:
            tunnel = ngrok.connect(5000, domain=domain)
        else:
            tunnel = ngrok.connect(5000)
            
        active_session['public_url'] = tunnel.public_url
        server_globals["ngrok_running"] = True
        save_state()
        print(f"[*] Live Tunnel Established: {active_session['public_url']}")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

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
    save_state()
    return jsonify({"status": "success", "public_url": active_session['public_url']})

@app.route('/download/agent')
def download_agent():
    master_path = os.path.join(app.root_path, 'static', 'MasterAgent.exe')
    if not os.path.exists(master_path):
        return "MasterAgent.exe missing. Please place it in the static folder.", 404
    clean_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', active_session['name'])
    return send_file(master_path, as_attachment=True, download_name=f"ProctoredExam_{clean_title}.exe")

# --- AGENT AUTO-HANDSHAKE & HEARTBEAT ---
@app.route('/api/agent_checkin', methods=['POST'])
def agent_checkin():
    token = request.json.get("token", "").strip() if request.json else ""
    if not token or not active_session['is_active']:
        return jsonify({"status": "error"}), 400
    if token not in active_agents:
        active_agents[token] = {"status": "waiting", "student_id": None, "last_seen": time.time(), "closed_flagged": False}
    else:
        active_agents[token]["last_seen"] = time.time()
    save_state()
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

    if not name or not sid or not token or token not in active_agents:
        return jsonify({"status": "error", "message": "Invalid request or agent missing."}), 400

    active_agents[token]["status"] = "active"
    active_agents[token]["student_id"] = sid

    existing = next((s for s in active_session['students'] if s['student_id'] == sid), None)
    if not existing:
        active_session['students'].append({
            "name": name, "student_id": sid, "email": email, "token": token, "status": "in_progress"
        })
    else:
        existing.update({"status": "in_progress", "token": token})
    save_state()
    return jsonify({"status": "success", "form_link": active_session['form_link']})

@app.route('/api/agent_heartbeat', methods=['POST'])
def agent_heartbeat():
    token = (request.json or {}).get("token", "").strip()
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
    sid = (request.json or {}).get('student_id', '').strip()
    for s in active_session['students']:
        if s['student_id'] == sid:
            s['status'] = 'completed'
            if s.get('token') in active_agents:
                active_agents[s['token']]["status"] = "completed"
            save_state()
            return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Student not found."}), 404

# --- VIOLATION LOGGING ---
@app.route('/log', methods=['POST'])
def log_violation():
    data = request.json or {}
    sid = data.get('student_id')
    student = next((s for s in active_session['students'] if s['student_id'] == sid), None)
    if student and student.get('status') == 'completed':
        return jsonify({"status": "ignored"}), 200

    active_session['logs'].append(data)
    save_state()
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
                        "student_id": sid, "category": "Agent Terminated",
                        "details": "[CRITICAL] Proctor agent was closed or process terminated during exam",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })
                    save_state()

    rows = []
    for s in active_session['students']:
        s_logs = [l for l in active_session['logs'] if l.get('student_id') == s['student_id']]
        rows.append({
            "name": s['name'], "student_id": s['student_id'], "status": s.get('status', 'in_progress'),
            "violations": len(s_logs),
            "details": " | ".join(set([l['details'] for l in s_logs])) if s_logs else "None"
        })
    return jsonify(rows)

@app.route('/api/end_session', methods=['POST'])
def end_session():
    active_session['is_active'] = False
    save_state()
    report = []
    for s in active_session['students']:
        s_logs = [l for l in active_session['logs'] if l.get('student_id') == s['student_id']]
        report.append({
            "Student Name": s['name'], "Student ID": s['student_id'], "Email": s['email'],
            "Status": s.get('status', 'completed').title(), "Total Violations": len(s_logs),
            "Violation Details": "\n".join([f"[{l.get('timestamp', '')}] {l['details']}" for l in s_logs]) if s_logs else "Clean"
        })

    df = pd.DataFrame(report) if report else pd.DataFrame(columns=["Student Name", "Student ID", "Email", "Status", "Total Violations", "Violation Details"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Exam Report")
    output.seek(0)

    return send_file(
        output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True, download_name=f"Exam_Report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    )

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:5000')).start()
    app.run(port=5000, use_reloader=False)