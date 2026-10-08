import os
import sys
import time
import ctypes
import threading
import requests
import tkinter as tk
from datetime import datetime

API_HEADERS = {
    "ngrok-skip-browser-warning": "69420",
    "User-Agent": "ProctorAgentClient/5.0"
}

# Targeted application signatures
KEYWORD_RULES = [
    (["chatgpt", "claude", "gemini", "copilot", "perplexity", "openai"], "AI Assistant"),
    (["word", "winword", "document - word"], "Microsoft Word"),
    (["notepad", "sticky notes", "onenote", "notes"], "Notes / Notepad"),
    (["pdf", "acrobat", "foxit"], "PDF Viewer"),
]

# Supported web browsers
BROWSERS = ["google chrome", "microsoft edge", "firefox", "brave", "opera", "vivaldi"]

# Whitelisted keywords for the official exam viewport
AUTHORIZED_EXAM_TOKENS = ["exam entry portal", "google forms", "google form"]

def get_active_window_title():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value.strip()
    except Exception:
        return ""

class RulesProctorAgent(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Exam Proctor Agent - Guidelines")
        self.geometry("520x420")
        self.resizable(False, False)
        self.eval('tk::PlaceWindow . center')
        self.configure(bg="#f8f9fa")

        self.server_url, self.token = self.parse_clipboard()
        self.student_id = ""
        self.is_monitoring = False
        self.last_flagged_title = ""

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close_attempt)

        if self.server_url and self.token:
            threading.Thread(target=self.lifecycle_loop, daemon=True).start()
        else:
            self.status_lbl.config(text="⚠️ Session data missing. Please download again from the portal.", fg="#dc3545")

    def parse_clipboard(self):
        try:
            clip = self.clipboard_get().strip()
            if "###" in clip:
                parts = clip.split("###")
                return parts[0].rstrip("/"), parts[1]
        except Exception:
            pass
        return "", ""

    def build_ui(self):
        tk.Label(self, text="🛡️ Examination Rules & Guidelines", font=("Arial", 14, "bold"), bg="#f8f9fa").pack(pady=(16, 6))

        rules_text = (
            "IMPORTANT RULES FOR THIS EXAMINATION:\n\n"
            "1. You may view this window anytime without penalty.\n\n"
            "2. Do not close this agent window until you finish your exam.\n"
            "   (Closing this program will immediately flag an exam violation)\n\n"
            "3. Keep all extra applications closed (Word, Notepad, PDFs, Notes).\n\n"
            "4. Switching to another browser tab or opening AI tools is forbidden.\n\n"
            "5. Return to your web browser to enter your details and begin."
        )
        tk.Label(self, text=rules_text, font=("Consolas", 9), fg="#1e293b", bg="#e2e8f0",
                 padx=14, pady=12, justify="left", relief="solid", borderwidth=1).pack(fill="x", padx=25, pady=10)

        status_box = tk.Frame(self, bg="#ffffff", relief="solid", borderwidth=1)
        status_box.pack(fill="x", padx=25, pady=8)

        self.status_lbl = tk.Label(status_box, text="Connecting to exam portal...", font=("Arial", 10, "bold"), fg="#0d6efd", bg="#ffffff")
        self.status_lbl.pack(pady=10)

    def on_close_attempt(self):
        """Triggered if the student manually closes the agent with X or Alt+F4."""
        if self.is_monitoring and self.student_id:
            try:
                requests.post(f"{self.server_url}/log", json={
                    "student_id": self.student_id,
                    "category": "Agent Terminated",
                    "details": "[CRITICAL] Proctor agent window was closed while exam in progress",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }, headers=API_HEADERS, timeout=3)
            except Exception:
                pass
        self.destroy()
        sys.exit(0)

    def lifecycle_loop(self):
        try:
            requests.post(f"{self.server_url}/api/agent_checkin", json={"token": self.token}, headers=API_HEADERS, timeout=5)
            self.status_lbl.config(text="🟢 Agent Live & Detected! Complete details in browser.", fg="#198754")
        except Exception:
            self.status_lbl.config(text="⚠️ Cannot reach exam server.", fg="#dc3545")
            return

        while True:
            try:
                res = requests.post(f"{self.server_url}/api/agent_heartbeat", 
                                    json={"token": self.token, "student_id": self.student_id}, 
                                    headers=API_HEADERS, timeout=4).json()
                
                status = res.get("status")
                sid = res.get("student_id")

                if status == "active" and not self.is_monitoring:
                    self.student_id = sid
                    self.is_monitoring = True
                    self.status_lbl.config(text=f"🟢 Monitoring Active (Student: {sid})", fg="#198754")
                    self.iconify()
                    threading.Thread(target=self.window_tracking_loop, daemon=True).start()

                elif status == "completed" or not res.get("session_active"):
                    self.is_monitoring = False
                    self.destroy()
                    sys.exit(0)

            except Exception:
                pass

            time.sleep(2)

    def window_tracking_loop(self):
        while self.is_monitoring:
            raw_title = get_active_window_title()
            title_lower = raw_title.lower()

            # Ignore transient empty titles
            if not raw_title:
                time.sleep(1.2)
                continue

            # 1. ALLOWED: The Proctor Agent guidelines window
            if "exam proctor agent" in title_lower:
                time.sleep(1.2)
                continue

            # 2. ALLOWED: The official exam portal and embedded Google Form
            is_authorized_tab = any(token in title_lower for token in AUTHORIZED_EXAM_TOKENS)
            if is_authorized_tab:
                time.sleep(1.2)
                continue

            # 3. VIOLATION: Everything else is strictly unauthorized
            category = "Unauthorized Application / Window"

            # Categorize specific apps if matched for clearer reporting
            for keywords, cat_name in KEYWORD_RULES:
                if any(k in title_lower for k in keywords):
                    category = cat_name
                    break

            # If it's a browser tab on any non-exam site
            if category == "Unauthorized Application / Window" and any(b in title_lower for b in BROWSERS):
                category = "Switched Tab / Other Webpage"

            # Log violation (debounced so it doesn't spam identical logs)
            if raw_title != self.last_flagged_title:
                self.last_flagged_title = raw_title
                payload = {
                    "student_id": self.student_id,
                    "category": category,
                    "details": f"[{category}] {raw_title}",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                try:
                    requests.post(f"{self.server_url}/log", json=payload, headers=API_HEADERS, timeout=3)
                except Exception:
                    pass

            time.sleep(1.2)

if __name__ == "__main__":
    app = RulesProctorAgent()
    app.mainloop()