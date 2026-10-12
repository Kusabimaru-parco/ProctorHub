## 🚀 Instructor Setup & Usage Guide

### 1. Prerequisites
* **Windows 10 / 11**
* **Python 3.10+** (You must check **"Add python.exe to PATH"** during installation).
* A free **Ngrok account**.

### 2. First-Time Launch
1. Download or clone this repository to your computer.
2. Double-click the `Start_Hub.bat` file.
3. The script will automatically verify your Python installation, install the required packages from `requirements.txt`, and launch your default web browser to the setup page.

### 3. Server Configuration
On the setup screen, you will be prompted for two keys from your free Ngrok account:
* **Auth Token:** Found under **Your Authtoken** in the Ngrok dashboard.
* **Static Domain:** Go to **Domains** in the left-hand menu of Ngrok and click **Create Domain**. Copy the generated URL (e.g., `upward-grizzly.ngrok-free.app`).
> **Note:** The system securely saves these in your browser so you only have to enter them once.

### 4. Running the Exam
1. Enter your **Exam / Class Name** and paste your **Google Forms Link**.
2. Click **Start Exam Session**.
3. Copy the generated **Student Portal Link** and distribute it to your class (via LMS, MS Teams, etc.).
4. Monitor the live dashboard. As students connect and begin the exam, their statuses and any violations will appear in real time.
5. When the exam is over, click **🛑 End Exam & Export Excel**. The system will instantly download the comprehensive violation report and return you to the session creation screen for your next class.

---

## 🎓 Student Experience

1. **Access:** The student opens the shared link on a Windows PC (mobile devices are blocked).
2. **Download:** The student clicks **Download Proctor Agent (.exe)**.
3. **SmartScreen Bypass:** Because this is an open-source educational tool, Windows Defender may show a blue prompt. An in-page visual guide instructs the student to click **More info** -> **Run anyway**.
4. **Auto-Link:** The agent displays the exam rules and minimizes. The web portal instantly detects the agent and unlocks the student details form.
5. **Exam:** The student enters their Name and ID, and the Google Form loads. If they open any other app or switch tabs, it is reported to the professor.
6. **Finish:** Once the form is submitted, the **Finish Exam** button unlocks. Clicking it silently closes the background agent and logs a successful completion.

---

## 🔍 Violation Detection Matrix

| Trigger | Category Logged | Details Captured |
| :--- | :--- | :--- |
| Focus on non-exam browser tab | `Switched Tab / Other Webpage` | Full tab title (e.g., `[Switched Tab] YouTube - Google Chrome`) |
| Opening ChatGPT, Claude, Gemini | `AI Assistant` | Window title (e.g., `[AI Assistant] ChatGPT - Mozilla Firefox`) |
| Opening Word / Document | `Microsoft Word` | Document name (e.g., `[Microsoft Word] Notes.docx - Word`) |
| Opening Notepad / Notes | `Notes / Notepad` | App name (e.g., `[Notes / Notepad] Untitled - Notepad`) |
| Opening PDF Files | `PDF Viewer` | Reader title (e.g., `[PDF Viewer] Chapter3.pdf - Acrobat`) |
| Any other unauthorized app | `Unauthorized Application / Window` | Exact window title of the open application |
| Closing `.exe` before finishing | `Agent Terminated` | `[CRITICAL] Proctor agent was closed or process terminated during exam` |

---

## 🛠️ For Developers: Modifying the Agent

If you modify `proctor_agent.py` to add new rules or change the GUI, you must recompile the executable before deploying it to students.

1. Open PowerShell in the project directory.
2. Run the PyInstaller command:
```powershell
python -m PyInstaller --onefile --noconsole --icon=logo.ico proctor_agent.py
🛡️ ProctorHub: Lightweight Exam Proctoring System
An open-source, zero-cost exam monitoring system designed for academic institutions. ProctorHub links a local Flask control server with a lightweight Windows desktop agent to enforce exam integrity during Google Forms exams—monitoring window focus, detecting unauthorized tools (ChatGPT, Word, Notes, PDFs, tab switches), and auto-exporting timestamped violation reports to Excel without requiring paid code-signing certificates.

📋 Features
Zero-Friction Student Pairing: No manual IP entry or PINs required. When students download the agent from the portal, connection tokens pair the running executable to the browser automatically.

Smart App & Tab Detection: Operates on an active-window allowlist. Flags unauthorized desktop apps (MS Word, Notepad, Sticky Notes, PDF readers), AI tools (ChatGPT, Claude, Gemini), and browser tab switching.

Whitelisted Guidelines: Students can safely bring the Proctor Agent window to the front at any time to review rules without triggering a false positive.

Tamper & Termination Watchdog: If a student attempts to close the .exe via the X button, Alt+F4, or Task Manager, a critical violation is recorded immediately.

Gated Exam Completion: Google Form is embedded inside a secure viewport. The Finish Exam button stays locked until the Google Form confirmation page is submitted, which automatically shuts down the desktop agent.

Instant Excel Reporting: Generates a structured .xlsx spreadsheet of all registered students, completion statuses, violation counts, and timestamped infraction details upon ending the session.

One-Click Instructor Launcher: Double-clicking Start_Hub.bat starts the server and automatically opens the dashboard in your default browser. Closing the dashboard tab cleanly terminates the server and background tunnels.



🚀 Instructor Quick Start Guide
1. Prerequisites
Windows 10 / 11

Python 3.10+ (ensure "Add python.exe to PATH" was checked during installation)

A free Ngrok Account (required to establish public tunnels outside your local network)

2. Initial Setup (One-Time Only)
Clone the repository:

Bash
git clone https://github.com/Kusabimaru-parco/ProctorHub.git
cd ProctorHub
Install dependencies:

Bash
pip install -r requirements.txt
Configure your free Ngrok Authtoken:

Sign up at ngrok.com and copy your Authtoken from the dashboard.

Run the following command in PowerShell/CMD:

Bash
python -c "from pyngrok import ngrok; ngrok.set_auth_token('YOUR_NGROK_TOKEN_HERE')"


3. Launching an Exam Session
Double-click Start_Hub.bat (or run python hub.py).

Your default web browser will automatically open http://localhost:5000.

Under Create Exam Session:

Enter the Exam / Class Name (e.g., BSIT 1-1 OOP Finals).

Paste your Google Forms Link.

Click Start Exam Session.

Copy the generated Student Portal Link (e.g., [https://xxxx-xx.ngrok-free.app/student](https://xxxx-xx.ngrok-free.app/student)) and distribute it to your students via your LMS or chat room.

4. Ending the Session & Exporting Data
Click 🛑 End Exam & Export Excel on the live dashboard.

The system will:

Terminate active student agents.

Kill the public ngrok tunnel.

Automatically download Exam_Report_YYYY-MM-DD_HH-MM-SS.xlsx directly to your browser.

Closing the dashboard browser tab will automatically shut down the hub.py background process.
