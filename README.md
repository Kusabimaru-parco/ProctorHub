# 🛡️ ProctorHub: Lightweight Exam Proctoring System

**ProctorHub** is a exam proctoring system designed for academic institutions and independent professors. It links a local Flask control server with a portable Windows desktop agent to enforce exam integrity during Google Forms assessments.

Designed for frictionless deployment, it features a one-click auto-installer, disconnection-proof networking, and strict window monitoring—without requiring commercial licenses or paid code-signing certificates.

---



## ✨ Key Features

* **One-Click Auto-Setup:** Instructors just double-click `Start_Hub.bat`. The script automatically verifies Python, installs missing dependencies, and opens the dashboard in the browser.
* **Disconnection-Proof Architecture:** Utilizes Ngrok Static Domains and local JSON state persistence. If your Wi-Fi drops or the server restarts, the exam session restores instantly without kicking students out.
* **Continuous Session Workflow:** Ending an exam exports the Excel report immediately and returns you to the session creation screen without shutting down the server.
* **Strict Window Allowlist:** The desktop agent explicitly blocks all applications except the official exam portal and the rules window. Switching to another browser tab, ChatGPT, Word, or PDFs flags an immediate violation.
* **Zero-PIN Auto-Pairing:** Students do not type IP addresses or PIN codes. Downloading the agent securely passes a background token that auto-links the `.exe` to their browser session within seconds.
* **Anti-Tamper Watchdog:** If a student forcefully closes the background proctor via the **X** button or Task Manager during an exam, the server logs a critical termination violation.

---
---
## Screenshots
### Host View
### Setting up account
<img width="1198" height="582" alt="image" src="https://github.com/user-attachments/assets/b7e2ff78-747c-47fc-959e-80a058595ae6" />

### Setting up session
<img width="1169" height="427" alt="image" src="https://github.com/user-attachments/assets/81f69793-9a7b-45d9-9df4-7ee097faf30e" />

### Live exam session
<img width="1137" height="550" alt="image" src="https://github.com/user-attachments/assets/edcbd961-f038-4391-9cdb-d1720339cb3a" />

### Student View
1. Student's view after clicking the link
   <img width="597" height="612" alt="image" src="https://github.com/user-attachments/assets/1f89b25b-e0f1-4312-b7bd-17b603210e22" />

2. The Proctor Agent 
   <img width="517" height="447" alt="image" src="https://github.com/user-attachments/assets/0a11f73c-fc51-40df-889f-81ae18ef4f2a" />

3. Exam View
   <img width="1342" height="632" alt="image" src="https://github.com/user-attachments/assets/c8913d97-a9f1-4529-bcd6-a26462f2d347" />

---

---
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
