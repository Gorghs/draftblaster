"""
FastAPI application entrypoint for Gmail Draft Auto-Sender.
Supports both Gmail App Password (IMAP/SMTP) and Google OAuth 2.0.
Features live countdown clock and interactive 'Send Now' trigger.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Security, status, Header, Query
from fastapi.responses import JSONResponse, HTMLResponse

from config import (
    PORT,
    HOST,
    TIMEZONE_STR,
    APP_TIMEZONE,
    SEND_HOUR,
    SEND_MINUTE,
    TRIGGER_SECRET,
    EMAIL_GMAIL_USER,
    EMAIL_GMAIL_PASSWORD,
    GOOGLE_CLIENT_ID,
    GOOGLE_REFRESH_TOKEN
)
from oauth_routes import router as oauth_router
from scheduler import evaluate_and_trigger, get_current_localized_time
from state_store import get_state_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown validation."""
    logger.info("Starting Gmail Draft Auto-Sender Service...")
    logger.info("Timezone: %s | Daily Target: %02d:%02d", TIMEZONE_STR, SEND_HOUR, SEND_MINUTE)
    
    if EMAIL_GMAIL_USER and EMAIL_GMAIL_PASSWORD:
        logger.info("Auth Mode: Gmail App Password active for %s.", EMAIL_GMAIL_USER)
    elif GOOGLE_CLIENT_ID and GOOGLE_REFRESH_TOKEN:
        logger.info("Auth Mode: Google OAuth 2.0 active with refresh token.")
    else:
        logger.warning("No complete credentials found. Configure App Password or OAuth in environment.")

    yield
    logger.info("Shutting down Gmail Draft Auto-Sender Service...")


app = FastAPI(
    title="Gmail Draft Auto-Sender",
    description="Automates sending all Gmail drafts at a configured daily time via App Password or OAuth.",
    version="2.3.0",
    lifespan=lifespan
)

# Mount OAuth routes (/oauth/login, /auth/login, etc.)
app.include_router(oauth_router)


def verify_trigger_secret(
    secret_param: Optional[str] = Query(None, alias="secret"),
    secret_header: Optional[str] = Header(None, alias="x-trigger-secret"),
    authorization: Optional[str] = Header(None)
) -> bool:
    """Validates trigger secret from query parameter or headers."""
    if not TRIGGER_SECRET:
        return True

    if secret_param and secret_param == TRIGGER_SECRET:
        return True

    if secret_header and secret_header == TRIGGER_SECRET:
        return True

    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1] == TRIGGER_SECRET:
            return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing trigger secret."
    )


@app.get("/", response_class=HTMLResponse, summary="Service Dashboard")
def dashboard():
    """Renders dashboard with live countdown clock and Send Now button."""
    now = get_current_localized_time()
    store = get_state_store()
    last_run = store.get_last_run_info()

    if EMAIL_GMAIL_USER and EMAIL_GMAIL_PASSWORD:
        auth_mode = "Gmail App Password"
        auth_status = f"✅ Active ({EMAIL_GMAIL_USER})"
    elif GOOGLE_REFRESH_TOKEN:
        auth_mode = "Google OAuth 2.0"
        auth_status = "✅ Active (Refresh Token Configured)"
    else:
        auth_mode = "None"
        auth_status = "⚠️ Missing Credentials (Set App Password or OAuth)"

    server_epoch_ms = int(now.timestamp() * 1000)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gmail Draft Auto-Sender</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background: #0b1120;
                color: #f8fafc;
                margin: 0;
                padding: 40px 16px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }}
            .card {{
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 32px;
                max-width: 660px;
                width: 100%;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
            }}
            .header {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 6px;
            }}
            .header h1 {{
                color: #38bdf8;
                margin: 0;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: -0.02em;
            }}
            .subtitle {{
                color: #94a3b8;
                font-size: 13px;
                margin: 0 0 24px 0;
            }}

            /* Live Countdown Clock Section */
            .clock-card {{
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                border: 1px solid #4f46e5;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                margin-bottom: 24px;
                box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.3);
            }}
            .clock-title {{
                color: #a5b4fc;
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 12px;
            }}
            .clock-grid {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 10px;
            }}
            .time-box {{
                display: flex;
                flex-direction: column;
                align-items: center;
                min-width: 68px;
            }}
            .time-val {{
                font-size: 34px;
                font-weight: 800;
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                color: #38bdf8;
                text-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
                line-height: 1;
            }}
            .time-lbl {{
                font-size: 10px;
                font-weight: 600;
                color: #94a3b8;
                letter-spacing: 0.06em;
                margin-top: 6px;
            }}
            .colon {{
                font-size: 28px;
                font-weight: 800;
                color: #818cf8;
                margin-bottom: 16px;
            }}

            /* Send Now Button Section */
            .action-section {{
                margin-bottom: 24px;
            }}
            .btn-send-now {{
                width: 100%;
                background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
                color: #ffffff;
                border: none;
                padding: 14px 24px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.4);
                transition: all 0.2s ease;
            }}
            .btn-send-now:hover:not(:disabled) {{
                transform: translateY(-1px);
                box-shadow: 0 15px 25px -3px rgba(2, 132, 199, 0.6);
                background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%);
            }}
            .btn-send-now:disabled {{
                background: #475569;
                color: #94a3b8;
                cursor: not-allowed;
                box-shadow: none;
            }}
            .result-banner {{
                margin-top: 12px;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                line-height: 1.4;
                display: none;
            }}
            .result-banner.success {{
                background: rgba(34, 197, 94, 0.15);
                border: 1px solid #22c55e;
                color: #86efac;
            }}
            .result-banner.error {{
                background: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444;
                color: #fca5a5;
            }}
            .result-banner.info {{
                background: rgba(14, 165, 233, 0.15);
                border: 1px solid #0ea5e9;
                color: #7dd3fc;
            }}

            /* Info Items Table */
            .info-table {{
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 12px 18px;
                margin-bottom: 20px;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 9px 0;
                border-bottom: 1px solid #1e293b;
                font-size: 13px;
            }}
            .info-row:last-child {{ border-bottom: none; }}
            .label {{ color: #94a3b8; font-weight: 500; }}
            .val {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: #f1f5f9; }}
            .badge-active {{ background: #166534; color: #bbf7d0; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}

            .footer-note {{
                font-size: 12px;
                color: #64748b;
                text-align: center;
                line-height: 1.5;
            }}
            code {{
                background: #0f172a;
                padding: 2px 6px;
                border-radius: 4px;
                color: #7dd3fc;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <span style="font-size: 28px;">🚀</span>
                <h1>Gmail Draft Auto-Sender</h1>
            </div>
            <p class="subtitle">Automated background service on Render triggered every minute by external uptime ping.</p>

            <!-- Live Clock Card -->
            <div class="clock-card">
                <div class="clock-title">⏱️ Time Left to Auto Draft Send (Hour : Minute : Second)</div>
                <div class="clock-grid">
                    <div class="time-box">
                        <span id="hoursVal" class="time-val">--</span>
                        <span class="time-lbl">HOURS</span>
                    </div>
                    <span class="colon">:</span>
                    <div class="time-box">
                        <span id="minsVal" class="time-val">--</span>
                        <span class="time-lbl">MINUTES</span>
                    </div>
                    <span class="colon">:</span>
                    <div class="time-box">
                        <span id="secsVal" class="time-val">--</span>
                        <span class="time-lbl">SECONDS</span>
                    </div>
                </div>
            </div>

            <!-- Instant Send Action Button -->
            <div class="action-section">
                <button id="sendBtn" class="btn-send-now" onclick="triggerSendNow()">
                    ⚡ Send Now (Instant Trigger)
                </button>
                <div id="resultBanner" class="result-banner"></div>
            </div>

            <!-- Status Details -->
            <div class="info-table">
                <div class="info-row">
                    <span class="label">Service Status:</span>
                    <span class="val"><span class="badge-active">Active</span></span>
                </div>
                <div class="info-row">
                    <span class="label">Auth Method:</span>
                    <span class="val">{auth_mode}</span>
                </div>
                <div class="info-row">
                    <span class="label">Auth Status:</span>
                    <span class="val">{auth_status}</span>
                </div>
                <div class="info-row">
                    <span class="label">Configured Timezone:</span>
                    <span class="val">{TIMEZONE_STR}</span>
                </div>
                <div class="info-row">
                    <span class="label">Current Server Time:</span>
                    <span class="val" id="serverClock">{now.strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="info-row">
                    <span class="label">Scheduled Send Time:</span>
                    <span class="val">{SEND_HOUR:02d}:{SEND_MINUTE:02d} ({TIMEZONE_STR})</span>
                </div>
                <div class="info-row">
                    <span class="label">Last Executed Date:</span>
                    <span class="val" id="lastExecDate">{last_run.get('last_send_date') or 'None recorded'}</span>
                </div>
            </div>

            <div class="footer-note">
                Uptime Endpoint: <code>GET /trigger?secret={TRIGGER_SECRET if TRIGGER_SECRET else 'YOUR_SECRET'}</code> (Ping every 1 minute)
            </div>
        </div>

        <script>
            // Server synchronization parameters
            const serverStartMs = {server_epoch_ms};
            const clientStartMs = Date.now();
            const targetHour = {SEND_HOUR};
            const targetMinute = {SEND_MINUTE};
            const triggerSecret = "{TRIGGER_SECRET}";

            function getServerNow() {{
                const elapsed = Date.now() - clientStartMs;
                return new Date(serverStartMs + elapsed);
            }}

            function updateCountdown() {{
                const now = getServerNow();

                // Format current server time
                const pad = (n) => String(n).padStart(2, '0');
                const yr = now.getFullYear();
                const mo = pad(now.getMonth() + 1);
                const da = pad(now.getDate());
                const hr = pad(now.getHours());
                const mi = pad(now.getMinutes());
                const sc = pad(now.getSeconds());
                document.getElementById('serverClock').innerText = `${{yr}}-${{mo}}-${{da}} ${{hr}}:${{mi}}:${{sc}}`;

                // Calculate target time today
                const targetToday = new Date(now.getTime());
                targetToday.setHours(targetHour, targetMinute, 0, 0);

                let diffMs = targetToday.getTime() - now.getTime();
                if (diffMs <= 0) {{
                    // If target today has already passed, countdown to tomorrow
                    const targetTomorrow = new Date(targetToday.getTime() + 24 * 60 * 60 * 1000);
                    diffMs = targetTomorrow.getTime() - now.getTime();
                }}

                const totalSeconds = Math.max(0, Math.floor(diffMs / 1000));
                const hours = Math.floor(totalSeconds / 3600);
                const minutes = Math.floor((totalSeconds % 3600) / 60);
                const seconds = totalSeconds % 60;

                document.getElementById('hoursVal').innerText = pad(hours);
                document.getElementById('minsVal').innerText = pad(minutes);
                document.getElementById('secsVal').innerText = pad(seconds);
            }}

            setInterval(updateCountdown, 1000);
            updateCountdown();

            // Send Now Button Click Handler
            async function triggerSendNow() {{
                if (!confirm('Are you sure you want to send all pending Gmail drafts now?')) {{
                    return;
                }}

                const btn = document.getElementById('sendBtn');
                const banner = document.getElementById('resultBanner');

                btn.disabled = true;
                btn.innerHTML = '⏳ Connecting & Sending Drafts...';
                banner.style.display = 'block';
                banner.className = 'result-banner info';
                banner.innerText = 'Connecting to Gmail... Please wait while drafts are sent.';

                try {{
                    const url = triggerSecret 
                        ? `/trigger?force=true&secret=${{encodeURIComponent(triggerSecret)}}`
                        : `/trigger?force=true`;

                    const res = await fetch(url);
                    const data = await res.json();

                    if (data.status === 'success') {{
                        const total = data.results?.total_drafts || 0;
                        const sent = data.results?.sent || 0;
                        const failed = data.results?.failed || 0;
                        banner.className = 'result-banner success';
                        banner.innerText = `✅ Batch Complete! Sent: ${{sent}} / ${{total}} draft(s). Failed: ${{failed}}.`;
                        if (data.date) {{
                            document.getElementById('lastExecDate').innerText = data.date;
                        }}
                    }} else if (data.status === 'idle') {{
                        banner.className = 'result-banner info';
                        banner.innerText = `ℹ️ Skipped: ${{data.message || data.reason || 'No action needed'}}`;
                    }} else {{
                        banner.className = 'result-banner error';
                        banner.innerText = `⚠️ Result: ${{data.error || data.message || JSON.stringify(data)}}`;
                    }}
                }} catch (err) {{
                    banner.className = 'result-banner error';
                    banner.innerText = `❌ Request failed: ${{err.message}}`;
                }} finally {{
                    setTimeout(() => {{
                        btn.disabled = false;
                        btn.innerHTML = '⚡ Send Now (Instant Trigger)';
                    }}, 4000);
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/health", summary="Basic Health Check")
def health_check():
    """Lightweight health check endpoint for Render. Returns 200 OK."""
    return {
        "status": "healthy",
        "service": "gmail-draft-auto-sender",
        "time": get_current_localized_time().isoformat()
    }


@app.get("/trigger", summary="Uptime Ping & Scheduled Trigger")
def trigger_endpoint(
    force: bool = Query(False, description="Force draft sending immediately for testing"),
    authorized: bool = Security(verify_trigger_secret)
):
    """
    Called every minute by an external uptime monitoring service.
    Validates trigger secret, verifies schedule window, prevents duplicate execution,
    and sends all drafts.
    """
    result = evaluate_and_trigger(force=force)
    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
