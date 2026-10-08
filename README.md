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
git clone https://github.com/your-username/ProctorHub.git
cd ProctorHub
Install dependencies:

Bash
pip install -r requirements.txt
Configure your free Ngrok Authtoken:

Sign up at ngrok.com and copy your Authtoken from the dashboard.

Run the following command in PowerShell/CMD:

Bash
python -c "from pyngrok import ngrok; ngrok.set_auth_token('YOUR_NGROK_TOKEN_HERE')"
(Optional) Compile the Master Agent:
If you modify proctor_agent.py or want to update the embedded logo.ico, recompile the master binary:

PowerShell
python -m PyInstaller --onefile --noconsole --icon=logo.ico proctor_agent.py
Move the resulting dist\proctor_agent.exe to static/MasterAgent.exe.

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
