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
