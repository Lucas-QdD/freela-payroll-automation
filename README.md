🚀 Freelance Payroll Automation (RPA)
📋 Overview
This project automates the weekly financial closing for an event management company. It replaces a manual, error-prone process of calculating payments for freelancers (photographers, LED technicians, etc.) with a reliable Python-based pipeline.

🛠️ Tech Stack
Language: Python 3.x

Data Manipulation: Pandas

Cloud Integration: Google Sheets API & Google Drive API (via gspread)

Authentication: Service Accounts with JSON credentials

Automation: GitHub Actions (Coming soon)

Report Generation: FPDF (Coming soon)

⚙️ How it Works
Cloud Sync: The script connects to a live Google Sheet used by the event managers.

Date Filtering: It automatically calculates the previous week's range (Monday to Sunday) using datetime.

Data Processing: Using Pandas, it aggregates multiple services performed by the same employee, calculating the total amount due.

Reporting: Generates individual PDF receipts and dispatches them via email (In progress).

📁 Project Structure
Plaintext
freela-payroll-automation/
├── src/
│   └── main.py          # Core logic and pipeline orchestration
├── requirements.txt     # Project dependencies
└── .env                 # Environment variables for sensitive data

🎯 Key Engineering Highlights
Scalability: Designed to handle a growing number of freelancers without manual intervention.

Security: Implements .gitignore and Environment Variables to protect API credentials and PII (Personally Identifiable Information).

Architecture: Clean code structure following the "Single Responsibility Principle" for data fetching and processing.
