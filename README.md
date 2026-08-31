# 🐍 DraftBlaster (Python Gmail API & Daily Scheduler Edition) 🚀

> **Production-Ready Python Automation Script Connecting Directly to Official Google Gmail API (v1) via OAuth 2.0 to Automatically Send Existing Drafts Daily at 9:00 AM (or on Demand).**  
> **Official Google OAuth 2.0 • Headless Daemon & Linux Cron Compatible • Token Auto-Refresh**

---

## 🔀 Repository Branch Guide

This repository provides three dedicated solutions for automating Gmail draft sending across different platforms:

| Branch | Platform / Edition | Purpose | When to Use |
|---|---|---|---|
| **`feature/gmail-api-scheduler`** *(You are here)* | **Python / Cloud / Server** | Standalone Python Script using Google Gmail API v1 & OAuth 2.0 | Use this branch if you want a backend / cron / server script that runs automatically at 9:00 AM. |
| **[`main`](https://github.com/Gorghs/draftblaster/tree/main)** | **Mozilla Firefox** | Native Firefox Manifest V3 Extension (`.xpi` / Temporary Add-on) | 👉 **Switch to the [`main`](https://github.com/Gorghs/draftblaster/tree/main) branch** for Firefox and Firefox Developer Edition. |
| **[`chrome-extension`](https://github.com/Gorghs/draftblaster/tree/chrome-extension)** | **Google Chrome & Chromium** | Manifest V3 Extension for Chrome, Opera, Brave, and Edge | 👉 **Switch to the [`chrome-extension`](https://github.com/Gorghs/draftblaster/tree/chrome-extension) branch** for Chrome, Opera, or Brave. |

---

## ⚙️ How it Works

Unlike browser extensions that simulate DOM clicks on the web UI, this script uses the **official Google Gmail API v1**:
1. **OAuth 2.0 Handshake**: Performs local browser authentication on first run and generates a persistent, secure `token.json`.
2. **Automatic Token Refresh**: Re-authenticates silently in the background when the token expires without requiring user interaction.
3. **Draft Retrieval**: Queries all available drafts in your account using `service.users().drafts().list()`.
4. **Automated Sending**: Sequentially sends each draft using `service.users().drafts().send(userId='me', body={'id': draft_id})` with human-safe delay pacing.
5. **Scheduled Execution**: Can run as a 24/7 daemon checking daily at **09:00 AM**, or be triggered by system cron / CI/CD pipelines.

---

## 🚀 Quick Setup & Installation

### Step 1: Clone Repository & Create Virtual Environment

```bash
# 1. Clone this branch
git clone -b feature/gmail-api-scheduler https://github.com/Gorghs/draftblaster.git
cd draftblaster

# 2. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install required dependencies
pip install -r requirements.txt
```

---

### Step 2: Configure Google Cloud OAuth 2.0 Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Gmail API** for your project.
3. Under **APIs & Services > Credentials**, create an **OAuth 2.0 Client ID** (Application type: *Desktop App*).
4. Download the credentials JSON and save it as `credentials.json` in this project directory:
   ```
   /path/to/draftblaster/credentials.json
   ```
   *(Alternatively, define `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` in a local `.env` file).*

---

### Step 3: Run First-Time Authorization

Run the script to authorize your Google account:

```bash
source .venv/bin/activate
python send_drafts.py --now
```

A browser window will open asking you to log into Google and grant Gmail permissions. Once granted, a `token.json` file is saved locally. **All future runs will execute headlessly with zero prompts!**

---

## 🚦 Execution Modes

### Mode 1: Daily 9:00 AM Scheduler Daemon
Keep the script running continuously in the background. It will automatically check and send drafts every day at 09:00 AM:

```bash
# Run daily at 09:00 AM
python send_drafts.py --schedule --time "09:00"

# Or run immediate send first, then stay active on 09:00 AM schedule
python send_drafts.py --schedule --now --time "09:00"
```

### Mode 2: Immediate One-Time Send
Sends all currently available drafts immediately and exits (perfect for manual runs or testing):

```bash
python send_drafts.py --now
```

### Mode 3: Linux / Server Cron Job
If hosting on a Linux server, VPS, or Raspberry Pi, add a standard crontab entry:

```bash
crontab -e
```
Add the following line to run every day at 9:00 AM:
```cron
0 9 * * * cd /path/to/draftblaster && /path/to/draftblaster/.venv/bin/python send_drafts.py --now >> /var/log/gmail_drafts.log 2>&1
```

---

## 🛡️ Security & Privacy

- **Protected by `.gitignore`**: `credentials.json`, `token.json`, and `.env` are strictly excluded from git tracking to prevent leaking private tokens.
- **Strict Error Handling**: Wrapped in try-except blocks with robust `HttpError` handling and status logs.
- **Drafts Preservation**: Drafts are sent cleanly through Gmail API v1 without modifying content, body, or attachments.
