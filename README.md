# 🐍 DraftBlaster (Python Gmail API & Daily Scheduler Edition) 🚀

<p align="center">
  <img src="public/icons/icon128.png" alt="DraftBlaster Logo" width="128" height="128" />
</p>

<p align="center">
  <strong>Production-Ready Python Automation Script Connecting Directly to Official Google Gmail API (v1) via OAuth 2.0 to Automatically Send Existing Drafts Daily at 9:00 AM (or on Demand).</strong>
</p>

<p align="center">
  <a href="https://github.com/Gorghs/draftblaster/blob/feature/gmail-api-scheduler/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=for-the-badge&logo=python" alt="Python 3.9+" /></a>
  <a href="https://developers.google.com/gmail/api"><img src="https://img.shields.io/badge/Google%20Gmail-API%20v1-red.svg?style=for-the-badge&logo=gmail" alt="Gmail API v1" /></a>
  <img src="https://img.shields.io/badge/Auth-OAuth%202.0%20PKCE-brightgreen.svg?style=for-the-badge" alt="OAuth 2.0" />
  <img src="https://img.shields.io/badge/Daemon-9%3A00%20AM%20Scheduler-orange.svg?style=for-the-badge" alt="9 AM Scheduler" />
</p>

---

## 🔀 Multi-Platform Repository Branches

DraftBlaster is engineered across three dedicated platform branches:

| Branch | Platform / Edition | Description | Quick Link |
|---|---|---|---|
| **`feature/gmail-api-scheduler`** *(Active)* | **🐍 Python / Cloud / Cron** | Headless Python Script using official Gmail API v1 & OAuth 2.0 (9:00 AM Scheduler) | [View Python Branch](https://github.com/Gorghs/draftblaster/tree/feature/gmail-api-scheduler) |
| **[`main`](https://github.com/Gorghs/draftblaster/tree/main)** | **🦊 Mozilla Firefox** | Native Firefox Manifest V3 Extension (`.xpi` installer & source) | [👉 Go to Firefox Branch](https://github.com/Gorghs/draftblaster/tree/main) |
| **[`chrome-extension`](https://github.com/Gorghs/draftblaster/tree/chrome-extension)** | **🌐 Google Chrome / Chromium** | Manifest V3 Extension for Chrome, Opera, Brave, and Edge | [👉 Go to Chrome Branch](https://github.com/Gorghs/draftblaster/tree/chrome-extension) |

---

## 🌟 Why Use the Python Gmail API Edition?

If you prefer automated, headless background scheduling on a server, VPS, Raspberry Pi, or cloud container (Docker/Railway/Render) without needing a browser window open:

- 🔑 **Official Google OAuth 2.0 Protocol**: Uses official Google APIs rather than legacy SMTP (which cannot access Gmail Drafts).
- 🔄 **Silent Token Auto-Refresh**: Tokens refresh automatically in the background without user intervention.
- ⏰ **9:00 AM Daily Scheduler Daemon**: Built-in scheduler daemon or system `cron` compatibility.
- 🛡️ **File Permission Hardening**: Access tokens are stored locally with `chmod 600` user-only permissions.
- ⚡ **Zero-Modification Policy**: Draft content, body, recipients, and attachments are transmitted 100% untouched.

---

## ⚡ Quick Setup & Installation

### Step 1: Clone Repository & Setup Virtual Environment

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

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Gmail API**.
3. Under **APIs & Services > Credentials**, create an **OAuth 2.0 Client ID** (*Desktop App*).
4. Download the JSON credentials file and save it as `credentials.json` in this project directory:
   ```
   /path/to/draftblaster/credentials.json
   ```
   *(Or define `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` in `.env`).*

---

### Step 3: First-Time Account Authorization

```bash
source .venv/bin/activate
python send_drafts.py --now
```

A browser window will open once to authorize your Google account. A `token.json` file is securely saved with `chmod 600` permissions. **All future runs will execute headlessly in the background!**

---

## 🚦 Execution Modes

### Mode 1: Daily 9:00 AM Scheduler Daemon
Runs continuously in the background, checking and sending drafts every day at 09:00 AM:

```bash
python send_drafts.py --schedule --time "09:00"
```

### Mode 2: Immediate One-Time Send
Sends all available drafts right now and exits:

```bash
python send_drafts.py --now
```

### Mode 3: Linux Crontab (Serverless / VPS)
```cron
0 9 * * * cd /path/to/draftblaster && /path/to/draftblaster/.venv/bin/python send_drafts.py --now >> /var/log/gmail_drafts.log 2>&1
```

---

## 🔒 Security & Privacy Architecture

- **Protected Secrets**: `credentials.json`, `token.json`, and `.env` are strictly excluded from source control via `.gitignore`.
- **Restricted Token Permissions**: Token file permissions are restricted to `0o600` (read/write only by file owner).
- **Read our complete [Security Policy](SECURITY.md)**.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
