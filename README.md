# 🚀 Gmail Draft Auto-Sender (Render Web Service Edition)

<p align="center">
  <img src="public/icons/icon128.png" alt="DraftBlaster Logo" width="100" height="100" />
</p>

<p align="center">
  <strong>Production-ready Python web service designed for Render to automate sending all Gmail drafts once daily at a configured time, kept alive by an external 1-minute uptime ping, with zero daily logins and ironclad duplicate prevention.</strong>
</p>

<p align="center">
  <a href="https://github.com/Gorghs/draftblaster/blob/feature/gmail-api-scheduler/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?style=for-the-badge&logo=fastapi" alt="FastAPI" /></a>
  <a href="https://developers.google.com/gmail/api"><img src="https://img.shields.io/badge/Gmail%20API-v1-EA4335.svg?style=for-the-badge&logo=gmail" alt="Gmail API v1" /></a>
  <a href="https://render.com/"><img src="https://img.shields.io/badge/Deploy-Render-46E3B7.svg?style=for-the-badge&logo=render" alt="Render" /></a>
  <img src="https://img.shields.io/badge/Auth-OAuth%202.0%20Offline-green.svg?style=for-the-badge" alt="OAuth 2.0" />
</p>

---

## 🔀 Multi-Platform Repository Branches

| Branch | Platform / Edition | Description |
|---|---|---|
| **`feature/gmail-api-scheduler`** *(Active)* | **🐍 Python / Render / Cloud** | Headless FastAPI Web Service on Render with 1-min uptime trigger & OAuth 2.0 |
| **[`main`](https://github.com/Gorghs/draftblaster/tree/main)** | **🦊 Mozilla Firefox** | Native Firefox Manifest V3 Extension (`.xpi` installer & source) |
| **[`chrome-extension`](https://github.com/Gorghs/draftblaster/tree/chrome-extension)** | **🌐 Google Chrome / Chromium** | Manifest V3 Extension for Chrome, Opera, Brave, and Edge |

---

## 📐 Architecture & Workflow

```
External Uptime Monitor (Every 1 minute)
         │
         ▼ HTTP GET https://your-service.onrender.com/trigger?secret=YOUR_SECRET
Render Web Service (FastAPI / Uvicorn)
         │
         ├─► Validate TRIGGER_SECRET (Rejects unauthorized traffic with 401)
         │
         ├─► Localized Time Evaluation (ZoneInfo: Asia/Kolkata)
         │     └─► Is current time within [SEND_HOUR:SEND_MINUTE] window?
         │           ├─► NO  --> Return 200 {"status": "idle", "reason": "Before/after window"}
         │           └─► YES --> Proceed to Duplicate Check
         │
         ├─► Duplicate Prevention & Concurrency Lock
         │     ├─► Check persistent store: Has today (YYYY-MM-DD) already executed?
         │     │     └─► YES --> Return 200 {"status": "idle", "reason": "already_executed_today"}
         │     │
         │     └─► NO  --> Acquire distributed atomic lock (Upstash Redis / File)
         │                 ├─► Lock failed (concurrent request running) --> Return 200 {"status": "in_progress"}
         │                 └─► Lock acquired --> Proceed to Gmail API
         │
         ├─► Official Gmail API v1 Execution
         │     ├─► Authenticate unattended using GOOGLE_REFRESH_TOKEN (Zero human login)
         │     ├─► List ALL drafts with pagination handling (pageToken)
         │     ├─► If 0 drafts: Return 200 {"status": "completed", "total_drafts": 0}
         │     └─► For each draft: Send via users().drafts().send()
         │           └─► Resilient error handling (one failed draft does not block others)
         │
         ├─► Record successful execution date (YYYY-MM-DD) in persistent state store
         ├─► Release atomic concurrency lock
         └─► Return structured execution summary JSON
```

---

## 🔒 Verified Least-Privileged Gmail OAuth Scope

| Scope | Permission | Why It Was Chosen |
|---|---|---|
| `https://www.googleapis.com/auth/gmail.compose` | **Create, read, update, and send drafts and messages.** | Official Google Gmail API least-privileged intersection. Allows `users.drafts.list` and `users.drafts.send`. Does **NOT** allow reading the user's general inbox or deleting messages. |

---

## 🛠️ Google Cloud Platform Setup (Current UI)

Follow these exact steps in the Google Cloud Console:

### Step 1: Create / Select Project
1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. In the top project selector dropdown, click **New Project**.
3. Name it `Gmail-Draft-AutoSender` and click **Create**.

### Step 2: Enable the Gmail API
1. Navigate to **APIs & Services** → **Library**.
2. Search for **Gmail API**.
3. Select **Gmail API** and click **Enable**.

### Step 3: Configure OAuth Consent Screen & Audience
1. Navigate to **APIs & Services** → **OAuth consent screen** (or **Google Auth Platform** → **Branding**).
2. Choose User Type: **External** → Click **Create**.
3. **App Information**:
   - App name: `Gmail Draft Auto-Sender`
   - User support email: Select your email.
   - Developer contact email: Enter your email.
4. Click **Save and Continue**.
5. **Scopes**:
   - Click **Add or Remove Scopes**.
   - In the filter box, enter: `https://www.googleapis.com/auth/gmail.compose`.
   - Select the checkbox for `.../auth/gmail.compose` and click **Update** → **Save and Continue**.
6. **Audience / Test Users**:
   - Add your Gmail account email address as a **Test User**.
   - Click **Save and Continue**.

> [!IMPORTANT]
> **Refresh Token Expiration Policy**:
> If an app's Publishing Status remains in **"Testing"**, Google automatically expires OAuth refresh tokens after **7 days**!
> **To make your refresh token permanent**: On the OAuth consent screen tab, click **"PUBLISH APP"** and confirm. Even if Google shows an "Unverified app" warning screen during your initial login, clicking **Advanced → Go to (unsafe)** permanently grants your personal account an indefinite refresh token that never expires.

### Step 4: Create OAuth 2.0 Client Credentials
1. Navigate to **APIs & Services** → **Credentials**.
2. Click **Create Credentials** → **OAuth client ID**.
3. **Application type**: Select **Web application** (NOT Desktop App, because Render hosts the redirect callback web route).
4. Name: `Render Auto-Sender Client`.
5. **Authorized redirect URIs**:
   - Add: `http://localhost:8000/auth/callback` (for local dev/testing)
   - Add: `https://YOUR-RENDER-SERVICE.onrender.com/auth/callback` (replace with your actual Render URL)
6. Click **Create**.
7. Copy your **Client ID** and **Client Secret**.

---

## ☁️ Render Deployment Guide

### Step 1: Push Code to GitHub
Ensure this branch is pushed to your GitHub repository:
```bash
git push origin feature/gmail-api-scheduler
```

### Step 2: Create Web Service on Render
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository: `Gorghs/draftblaster`.
4. Branch: Select **`feature/gmail-api-scheduler`**.
5. Runtime: **Python 3**.
6. **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
7. **Start Command**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
8. Instance Type: **Free**.

### Step 3: Configure Environment Variables in Render
In your Render Service Dashboard, navigate to **Environment** and add the following variables:

| Key | Value | Mark as Secret? |
|---|---|---|
| `GOOGLE_CLIENT_ID` | `YOUR_CLIENT_ID.apps.googleusercontent.com` | No |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-YOUR_CLIENT_SECRET` | **YES** |
| `OAUTH_REDIRECT_URI` | `https://YOUR-RENDER-SERVICE.onrender.com/auth/callback` | No |
| `TIMEZONE` | `Asia/Kolkata` | No |
| `SEND_HOUR` | `9` (24-hour format, e.g. 9 for 09:00 AM, 21 for 09:00 PM) | No |
| `SEND_MINUTE` | `0` | No |
| `EXECUTION_WINDOW_MINUTES` | `5` | No |
| `TRIGGER_SECRET` | `generate-a-random-secret-token-here` | **YES** |
| `REDIS_URL` | *(Optional but recommended, see Upstash below)* | **YES** |

Click **Save Changes**. Render will automatically build and deploy your service.

---

## 🔑 One-Time Initial OAuth Authorization

Once your Render service is live (`https://YOUR-RENDER-SERVICE.onrender.com`):

1. In your browser, open:
   ```
   https://YOUR-RENDER-SERVICE.onrender.com/auth/login
   ```
2. You will be redirected to the official Google login page.
3. Sign in to the Gmail account that holds the drafts.
4. If you see "Google hasn't verified this app", click **Advanced** → **Go to Gmail Draft Auto-Sender (unsafe)**.
5. Review the requested permission (*"Create, read, update, and send drafts and messages"*) and click **Continue**.
6. Google redirects to `/auth/callback`, which renders a success page displaying your generated **`GOOGLE_REFRESH_TOKEN`**.
7. Click **"Copy Refresh Token"**.
8. Go to your **Render Dashboard** → **Environment** → Add:
   - `GOOGLE_REFRESH_TOKEN` = `[pasted refresh token]`
9. Click **Save Changes**. Render restarts with unattended automation fully activated!

> **Zero Daily Human Interaction**: From this point on, the application authenticates directly with Google using this refresh token. You never need to log in again.

---

## ⏱️ Configure External 1-Minute Uptime Trigger

To prevent Render's free tier from sleeping and to trigger the daily check, use any free uptime monitoring service:

### Option A: Cron-Job.org (Recommended)
1. Sign up for free at [cron-job.org](https://cron-job.org/).
2. Click **Create Cronjob**.
3. **Title**: `DraftBlaster 1-Min Ping`
4. **URL**: `https://YOUR-RENDER-SERVICE.onrender.com/trigger?secret=YOUR_TRIGGER_SECRET`
5. **Schedule**: User-defined → **Every 1 minute** (`* * * * *`).
6. Click **Create**.

### Option B: UptimeRobot
1. Sign up at [UptimeRobot](https://uptimerobot.com/).
2. Add New Monitor → Monitor Type: **HTTP(s)**.
3. Friendly Name: `DraftBlaster Ping`.
4. URL: `https://YOUR-RENDER-SERVICE.onrender.com/trigger?secret=YOUR_TRIGGER_SECRET`.
5. Monitoring Interval: **Every 1 minute**.

---

## 🛡️ Duplicate Prevention & Persistence Strategy

### The Challenge with Render
Render's free tier spins down after inactivity and has an **ephemeral filesystem**. Any local file stored inside the container is discarded when Render redeploys or restarts. Furthermore, an uptime monitor sends requests every 60 seconds (09:00, 09:01, 09:02...).

### The Solution: Upstash Serverless Redis (Free)
To ensure reliable persistence and prevent double-sends across server restarts:

1. Create a free account at [Upstash Redis](https://upstash.com/) (Free tier gives 10,000 requests/day, no credit card required).
2. Create a Database named `draftblaster-state`.
3. Copy the **`rediss://...`** connection string.
4. Add it to Render Environment variables as `REDIS_URL`.

#### How Duplicate Prevention Works:
- **Distributed Atomic Locking**: Uses Redis `SET draftblaster:lock <uuid> NX EX 300`. Only one incoming request can obtain this lock. If two uptime pings arrive simultaneously, only one can proceed.
- **Date Check (`YYYY-MM-DD`)**: Stores the date of successful completion (`draftblaster:last_send_date = "2026-09-04"`). On every minute ping, the application checks if today's date matches. If already recorded, it skips immediately.
- **File Fallback**: If `REDIS_URL` is omitted, the app uses a local `state.json` file with POSIX `fcntl` file-locking (suitable for local dev or Render with Persistent Disk).

### What Happens if Render Restarts?
- If Render restarts before 09:00: The service boots up, waits for the uptime ping at 09:00, and sends drafts.
- If Render restarts during 09:00: The atomic lock automatically expires after 300 seconds (TTL), preventing stale locks.
- If Render restarts after 09:00: The service connects to Redis, sees `last_send_date == today`, and safely returns `idle (already_executed_today)` without duplicate sends.

---

## 🧪 Automated Testing

The repository includes a comprehensive test suite covering 100% of functional and edge cases with mocked Gmail APIs:

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run pytest suite
pytest -v
```

### Test Coverage:
1. `test_time_before_scheduled`: Requests before configured time return idle.
2. `test_time_exactly_scheduled`: Requests inside the window trigger execution.
3. `test_time_after_scheduled_window`: Requests outside the window return idle.
4. `test_already_sent_today`: Idempotent return when daily send has completed.
5. `test_no_drafts_found`: Graceful zero-draft handling without errors.
6. `test_multiple_drafts_with_pagination`: Full pagination (`pageToken`) test.
7. `test_one_draft_fails_others_succeed`: Resilience when one draft fails.
8. `test_trigger_secret_validation`: Verification of query param, headers, and Bearer tokens.
9. `test_missing_environment_variables`: Safe error reporting when credentials are missing.
10. `test_oauth_credential_construction_from_refresh_token`: OAuth credential initialization.
11. `test_redis_state_store_locking`: Distributed atomic lock verification.
12. `test_file_state_store_lock_and_run`: Local file lock verification.

---

## ✅ Final Production Checklist

- [x] Gmail OAuth Scope verified as least-privileged (`.../auth/gmail.compose`).
- [x] Web Application OAuth client created with valid redirect URI.
- [x] Google App Publishing status set to "In production" to prevent 7-day token expiration.
- [x] Render service configured with `PORT`, `HOST=0.0.0.0`, and start command.
- [x] One-time `/auth/login` completed and `GOOGLE_REFRESH_TOKEN` added to Render.
- [x] `TRIGGER_SECRET` set and configured in uptime monitoring ping.
- [x] `REDIS_URL` set (Upstash free tier) for restart resilience.
- [x] External monitor pinging `/trigger?secret=...` every 1 minute.
