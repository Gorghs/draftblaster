# 🚀 Gmail Draft Auto-Sender (Gmail App Password Edition)

<p align="center">
  <img src="public/icons/icon128.png" alt="DraftBlaster Logo" width="100" height="100" />
</p>

<p align="center">
  <strong>FastAPI background automation service on Render that automatically sends all Gmail drafts once daily at a configured time, triggered by an external 1-minute uptime ping, using a simple Gmail App Password.</strong>
</p>

<p align="center">
  <a href="https://github.com/Gorghs/draftblaster/blob/feature/gmail-api-scheduler/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?style=for-the-badge&logo=fastapi" alt="FastAPI" /></a>
  <a href="https://render.com/"><img src="https://img.shields.io/badge/Deploy-Render-46E3B7.svg?style=for-the-badge&logo=render" alt="Render" /></a>
  <img src="https://img.shields.io/badge/Auth-Gmail%20App%20Password-green.svg?style=for-the-badge" alt="App Password" />
  <img src="https://img.shields.io/badge/No%20GCP-Zero%20OAuth%20Setup-purple.svg?style=for-the-badge" alt="Zero GCP" />
</p>

---

## 💡 Why This Approach is 100x Simpler

| Feature | OAuth 2.0 (Google Cloud Console) | Gmail App Password (This Edition) |
|---|---|---|
| **Setup Time** | 20–30 mins (GCP project, consent screens, redirect URIs) | **1 minute** (Generate 16-character app password) |
| **Google Cloud Console Required?** | Yes, complex UI | **No** |
| **Token Expirations** | Yes (7-day expiration unless app is published) | **Never expires** until revoked |
| **Redirect URI Matching Issues** | Prone to `redirect_uri_mismatch` errors | **None** |
| **Draft Management** | Official REST API | **IMAP + SMTP** (Reads `[Gmail]/Drafts`, sends via SMTP, removes sent drafts) |

---

## 📐 How It Works

1. **Keep-Alive & Scheduling**: An external uptime monitor (e.g. cron-job.org or UptimeRobot) calls `GET /trigger?secret=YOUR_SECRET` every minute to keep Render awake.
2. **Timezone Evaluation**: The application checks current localized time (e.g. `09:00` in `Asia/Kolkata`).
3. **Duplicate Prevention**: Before sending, the service verifies that today's date (`YYYY-MM-DD`) has not already executed.
4. **Draft Retrieval & Send**:
   - Connects to `imap.gmail.com:993` with SSL using your `EMAIL_GMAIL_USER` and `EMAIL_GMAIL_PASSWORD`.
   - Locates and opens the `[Gmail]/Drafts` folder.
   - For each draft, parses recipients, subject, body, and attachments.
   - Connects to `smtp.gmail.com:587` with TLS and sends the email.
   - Marks the draft as deleted in IMAP so it leaves the Drafts folder (matching native Gmail behavior).
5. **Records Success**: Stores today's completion in persistent state (Upstash Redis or persistent file) to prevent re-sending on subsequent pings.

---

## 🔑 How to Generate a Gmail App Password (1 Minute)

1. Open your [Google Account Security Settings](https://myaccount.google.com/security).
2. Ensure **2-Step Verification** is turned **ON** on your account.
3. Open the [Google App Passwords Page](https://myaccount.google.com/apppasswords).
4. Enter an App Name (e.g., `DraftBlaster` or `Render`).
5. Click **Create**.
6. Google will display a **16-character password** (e.g. `abcd efgh ijkl mnop`).
7. Copy this password (without spaces) and use it as `EMAIL_GMAIL_PASSWORD`.

---

## ☁️ Render Deployment Instructions

### 1. Render Web Service Settings:
- **Runtime**: `Python 3`
- **Branch**: `feature/gmail-api-scheduler`
- **Root Directory**: *(Leave empty)*
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- **Instance Type**: `Free`

### 2. Environment Variables on Render:
Go to your Render service → **Environment** → click **"Add from .env"** and paste:

```env
EMAIL_GMAIL_USER=your_gmail_address@gmail.com
EMAIL_GMAIL_PASSWORD=abcdefghijklmnop
TIMEZONE=Asia/Kolkata
SEND_HOUR=9
SEND_MINUTE=0
EXECUTION_WINDOW_MINUTES=5
TRIGGER_SECRET=generate_any_secret_token_here
```

Click **Save Changes**. Render will automatically build and start the service!

---

## ⏱️ Configure External 1-Minute Uptime Trigger

To keep the Render free tier awake and trigger the daily check:

1. Sign up for free at [cron-job.org](https://cron-job.org/) (or [UptimeRobot](https://uptimerobot.com/)).
2. Create a new job:
   - **URL**: `https://YOUR-RENDER-SERVICE.onrender.com/trigger?secret=YOUR_SECRET`
   - **Interval**: **Every 1 minute** (`* * * * *`)
   - **Method**: `GET`
3. Save the job.

---

## 🛡️ Duplicate Prevention & Redis Persistence

To prevent duplicate sends across Render restarts or multiple minute pings:
- **Upstash Redis (Recommended)**: Create a free Redis database at [upstash.com](https://upstash.com/) and add `REDIS_URL` in Render. It provides distributed atomic locks (`SETNX`) and persistent date recording.
- **File Fallback**: If `REDIS_URL` is omitted, the app uses a local `state.json` file with POSIX `fcntl` file locking.

---

## 🧪 Testing Locally

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run automated test suite
pytest -v

# 3. Check schedule status via CLI
python send_drafts.py --check

# 4. Start local web server
uvicorn main:app --reload --port 8000
```
