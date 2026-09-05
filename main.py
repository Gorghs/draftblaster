"""
FastAPI application entrypoint for Gmail Draft Auto-Sender.
Supports both Gmail App Password (IMAP/SMTP) and Google OAuth 2.0.
Features Minecraft black-themed GUI, live countdown clock, interactive 'Send Now' button,
and live in-browser server log console.
"""

import os
import json
import logging
import collections
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

# Configure base logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)


# In-memory ring buffer log handler for live dashboard UI
class InMemoryLogHandler(logging.Handler):
    """Stores recent logs in memory for the Minecraft dashboard UI."""
    def __init__(self, capacity: int = 150):
        super().__init__(level=logging.INFO)
        self.logs = collections.deque(maxlen=capacity)

    def emit(self, record):
        try:
            self.logs.append({
                "time": datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage()
            })
        except Exception:
            self.handleError(record)


log_buffer = InMemoryLogHandler(capacity=150)
log_buffer.setLevel(logging.INFO)
logging.getLogger().addHandler(log_buffer)
logger.addHandler(log_buffer)
for mod_name in ("scheduler", "gmail_service", "state_store", "oauth_routes"):
    _mod_logger = logging.getLogger(mod_name)
    _mod_logger.setLevel(logging.INFO)
    _mod_logger.addHandler(log_buffer)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown validation."""
    logger.info("Starting Gmail Draft Auto-Sender Minecraft Service...")
    logger.info("Timezone: %s | Daily Target: %02d:%02d", TIMEZONE_STR, SEND_HOUR, SEND_MINUTE)

    if EMAIL_GMAIL_USER and EMAIL_GMAIL_PASSWORD:
        logger.info("Auth Mode: Gmail App Password active for %s.", EMAIL_GMAIL_USER)
    elif GOOGLE_CLIENT_ID and GOOGLE_REFRESH_TOKEN:
        logger.info("Auth Mode: Google OAuth 2.0 active with refresh token.")
    else:
        logger.warning("No complete credentials found. Configure App Password or OAuth in environment.")

    yield
    logger.info("Shutting down Gmail Draft Auto-Sender Minecraft Service...")


app = FastAPI(
    title="Gmail Draft Auto-Sender",
    description="Automates sending all Gmail drafts at a configured daily time via App Password or OAuth.",
    version="2.4.0",
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
    """Renders dashboard in black Minecraft theme with live countdown clock, Send Now, and log console."""
    now = get_current_localized_time()
    store = get_state_store()
    last_run = store.get_last_run_info()

    if EMAIL_GMAIL_USER and EMAIL_GMAIL_PASSWORD:
        auth_mode = "Gmail App Password"
        auth_status = f"Active ({EMAIL_GMAIL_USER})"
    elif GOOGLE_REFRESH_TOKEN:
        auth_mode = "Google OAuth 2.0"
        auth_status = "Active (Refresh Token Configured)"
    else:
        auth_mode = "None"
        auth_status = "Missing Credentials (Set App Password or OAuth)"

    server_epoch_ms = int(now.timestamp() * 1000)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Gmail Draft Auto-Sender</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            image-rendering: pixelated;
        }}

        body {{
            font-family: 'Press Start 2P', monospace, sans-serif;
            -webkit-font-smoothing: none;
            -moz-osx-font-smoothing: grayscale;
            font-smooth: never;
            background-color: #070707;
            background-image: 
                radial-gradient(#181818 15%, transparent 16%),
                radial-gradient(#181818 15%, transparent 16%);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
            color: #ffffff;
            margin: 0;
            padding: 30px 14px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}

        .mc-card {{
            background: #141414;
            border: 4px solid #000000;
            box-shadow: 
                inset 4px 4px #333333,
                inset -4px -4px #1c1c1c,
                0 0 0 4px #262626,
                0 20px 45px rgba(0, 0, 0, 0.95);
            padding: 26px 22px;
            max-width: 680px;
            width: 100%;
        }}

        .mc-header {{
            text-align: center;
            margin-bottom: 22px;
        }}

        .mc-title {{
            color: #55ff55;
            font-size: 15px;
            line-height: 1.5;
            margin: 0 0 10px 0;
            text-shadow: 2px 2px #003300, 3px 3px #000000;
            letter-spacing: 0.04em;
        }}

        .mc-subtitle {{
            color: #aaaaaa;
            font-size: 8px;
            line-height: 1.7;
            margin: 0;
            text-shadow: 1px 1px #000000;
        }}

        /* Minecraft Countdown Clock Panel */
        .mc-clock-panel {{
            background: #0a0a0a;
            border-top: 3px solid #000000;
            border-left: 3px solid #000000;
            border-right: 3px solid #333333;
            border-bottom: 3px solid #333333;
            padding: 18px 12px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: inset 2px 2px #050505;
        }}

        .mc-clock-title {{
            color: #ffaa00;
            font-size: 9px;
            line-height: 1.5;
            margin-bottom: 14px;
            text-shadow: 1px 1px #000000;
            letter-spacing: 0.05em;
        }}

        .mc-clock-grid {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }}

        .mc-slot {{
            background: #060606;
            border-top: 3px solid #000000;
            border-left: 3px solid #000000;
            border-right: 3px solid #3a3a3a;
            border-bottom: 3px solid #3a3a3a;
            padding: 12px 8px;
            min-width: 82px;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: inset 2px 2px #000000;
        }}

        .mc-digit {{
            font-size: 24px;
            color: #55ffff;
            text-shadow: 2px 2px #003333, 3px 3px #000000;
            line-height: 1.1;
            font-family: 'Press Start 2P', monospace;
        }}

        .mc-unit {{
            font-size: 8px;
            color: #aaaaaa;
            margin-top: 8px;
            text-shadow: 1px 1px #000000;
            letter-spacing: 0.05em;
        }}

        .mc-colon {{
            font-size: 22px;
            color: #ffaa00;
            text-shadow: 2px 2px #000000;
            padding-bottom: 14px;
            font-family: 'Press Start 2P', monospace;
        }}

        /* Minecraft 3D Stone Button */
        .mc-action-section {{
            margin-bottom: 20px;
        }}

        .mc-btn-send {{
            width: 100%;
            font-family: 'Press Start 2P', monospace;
            font-size: 11px;
            line-height: 1.4;
            padding: 14px 16px;
            background: #2c2c2c;
            color: #ffffff;
            text-shadow: 2px 2px #000000;
            border-top: 4px solid #666666;
            border-left: 4px solid #666666;
            border-right: 4px solid #111111;
            border-bottom: 4px solid #111111;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            user-select: none;
        }}

        .mc-btn-send:hover:not(:disabled) {{
            background: #3b3b3b;
            border-top-color: #888888;
            border-left-color: #888888;
            border-right-color: #1a1a1a;
            border-bottom-color: #1a1a1a;
            color: #ffff55;
            outline: 2px solid #ffffff;
        }}

        .mc-btn-send:active:not(:disabled) {{
            border-top: 4px solid #111111;
            border-left: 4px solid #111111;
            border-right: 4px solid #666666;
            border-bottom: 4px solid #666666;
            transform: translateY(2px);
        }}

        .mc-btn-send:disabled {{
            background: #181818;
            color: #555555;
            border-color: #333333 #0a0a0a #0a0a0a #333333;
            cursor: not-allowed;
            text-shadow: none;
            outline: none;
        }}

        /* Result Banner (Minecraft Chat / Achievement) */
        .mc-banner {{
            margin-top: 12px;
            padding: 10px 12px;
            font-size: 8px;
            line-height: 1.7;
            border: 3px solid #000000;
            display: none;
        }}

        .mc-banner.success {{
            background: #0b2612;
            border-color: #55ff55;
            color: #55ff55;
            box-shadow: inset 2px 2px #185c27;
        }}

        .mc-banner.error {{
            background: #2b0c0c;
            border-color: #ff5555;
            color: #ff5555;
            box-shadow: inset 2px 2px #5c1818;
        }}

        .mc-banner.info {{
            background: #09202b;
            border-color: #55ffff;
            color: #55ffff;
            box-shadow: inset 2px 2px #144963;
        }}

        /* Info Table (Minecraft Lore / Tooltip Box) */
        .mc-info-box {{
            background: #0a0a0a;
            border-top: 3px solid #000000;
            border-left: 3px solid #000000;
            border-right: 3px solid #2e2e2e;
            border-bottom: 3px solid #2e2e2e;
            padding: 14px 16px;
            margin-bottom: 20px;
            box-shadow: inset 2px 2px #040404;
        }}

        .mc-info-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 2px dashed #1a1a1a;
            font-size: 8px;
            line-height: 1.6;
        }}

        .mc-info-row:last-child {{
            border-bottom: none;
        }}

        .mc-label {{
            color: #aaaaaa;
            text-shadow: 1px 1px #000000;
        }}

        .mc-val {{
            color: #ffffff;
            text-shadow: 1px 1px #000000;
            text-align: right;
        }}

        .mc-badge {{
            background: #00aa00;
            color: #ffffff;
            border: 2px solid #55ff55;
            padding: 2px 6px;
            font-size: 8px;
            text-shadow: 1px 1px #000000;
            display: inline-block;
        }}

        /* Minecraft Console / Log Viewer */
        .mc-console-section {{
            margin-bottom: 20px;
        }}

        .mc-console-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .mc-console-title {{
            font-size: 9px;
            color: #55ffff;
            text-shadow: 1px 1px #000000;
        }}

        .mc-console-actions {{
            display: flex;
            gap: 6px;
        }}

        .mc-btn-mini {{
            font-family: 'Press Start 2P', monospace;
            font-size: 7px;
            padding: 4px 8px;
            background: #242424;
            color: #ffffff;
            border-top: 2px solid #555555;
            border-left: 2px solid #555555;
            border-right: 2px solid #111111;
            border-bottom: 2px solid #111111;
            cursor: pointer;
            text-shadow: 1px 1px #000000;
        }}

        .mc-btn-mini:hover {{
            background: #333333;
            color: #ffff55;
        }}

        .mc-console-body {{
            background: #050505;
            border-top: 3px solid #000000;
            border-left: 3px solid #000000;
            border-right: 3px solid #333333;
            border-bottom: 3px solid #333333;
            padding: 10px;
            height: 180px;
            overflow-y: auto;
            font-size: 8px;
            line-height: 1.8;
            box-shadow: inset 2px 2px #000000;
        }}

        .mc-console-body::-webkit-scrollbar {{
            width: 6px;
            background: #0a0a0a;
        }}

        .mc-console-body::-webkit-scrollbar-thumb {{
            background: #2a2a2a;
            border: 1px solid #444444;
        }}

        .log-line {{
            margin-bottom: 4px;
            word-break: break-word;
        }}

        .log-time {{ color: #777777; }}
        .log-name {{ color: #ffaa00; }}
        .log-lvl-INFO {{ color: #55ff55; }}
        .log-lvl-WARNING {{ color: #ffff55; }}
        .log-lvl-ERROR {{ color: #ff5555; }}
        .log-msg {{ color: #e0e0e0; }}

        /* Footer Note */
        .mc-footer {{
            font-size: 8px;
            color: #666666;
            text-align: center;
            line-height: 1.7;
            text-shadow: 1px 1px #000000;
        }}

        .mc-code {{
            color: #ffaa00;
            background: #000000;
            border: 1px solid #222222;
            padding: 2px 6px;
            display: inline-block;
            margin-top: 6px;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="mc-card">
        <div class="mc-header">
            <h1 class="mc-title">⚔️ GMAIL DRAFT AUTO-SENDER ⚔️</h1>
            <p class="mc-subtitle">Automated background service on Render triggered every minute by uptime ping.</p>
        </div>

        <!-- Live Clock Panel (Minecraft HUD Item Slots) -->
        <div class="mc-clock-panel">
            <div class="mc-clock-title">⏱️ TIME LEFT TO AUTO DRAFT SEND (HH : MM : SS)</div>
            <div class="mc-clock-grid">
                <div class="mc-slot">
                    <span id="hoursVal" class="mc-digit">--</span>
                    <span class="mc-unit">HOURS</span>
                </div>
                <span class="mc-colon">:</span>
                <div class="mc-slot">
                    <span id="minsVal" class="mc-digit">--</span>
                    <span class="mc-unit">MINUTES</span>
                </div>
                <span class="mc-colon">:</span>
                <div class="mc-slot">
                    <span id="secsVal" class="mc-digit">--</span>
                    <span class="mc-unit">SECONDS</span>
                </div>
            </div>
        </div>

        <!-- Minecraft 3D Button Section -->
        <div class="mc-action-section">
            <button id="sendBtn" class="mc-btn-send" onclick="triggerSendNow()">
                ⚡ SEND NOW (INSTANT TRIGGER)
            </button>
            <div id="resultBanner" class="mc-banner"></div>
        </div>

        <!-- Live Server Log Console Section -->
        <div class="mc-console-section">
            <div class="mc-console-header">
                <span class="mc-console-title">>_ SERVER LOGS [LIVE]</span>
                <div class="mc-console-actions">
                    <button id="btnAutoRefresh" class="mc-btn-mini" onclick="toggleAutoRefresh()">AUTO: ON</button>
                    <button class="mc-btn-mini" onclick="fetchLogs()">REFRESH</button>
                    <button class="mc-btn-mini" onclick="clearConsoleView()">CLEAR</button>
                </div>
            </div>
            <div id="mcConsole" class="mc-console-body">
                <div class="log-line" style="color: #666;">Loading server logs...</div>
            </div>
        </div>

        <!-- Minecraft Info & Status Box -->
        <div class="mc-info-box">
            <div class="mc-info-row">
                <span class="mc-label">SERVICE STATUS:</span>
                <span class="mc-val"><span class="mc-badge">ACTIVE</span></span>
            </div>
            <div class="mc-info-row">
                <span class="mc-label">AUTH METHOD:</span>
                <span class="mc-val">{auth_mode}</span>
            </div>
            <div class="mc-info-row">
                <span class="mc-label">AUTH STATUS:</span>
                <span class="mc-val">{auth_status}</span>
            </div>
            <div class="mc-info-row">
                <span class="mc-label">TIMEZONE:</span>
                <span class="mc-val">{TIMEZONE_STR}</span>
            </div>
            <div class="mc-info-row">
                <span class="mc-label">SERVER TIME:</span>
                <span class="mc-val" id="serverClock">{now.strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            <div class="mc-info-row">
                <span class="mc-label">SCHEDULED TIME:</span>
                <span class="mc-val">{SEND_HOUR:02d}:{SEND_MINUTE:02d} ({TIMEZONE_STR})</span>
            </div>
            <div class="mc-info-row">
                <span class="mc-label">LAST EXECUTED:</span>
                <span class="mc-val" id="lastExecDate">{last_run.get('last_send_date') or 'None recorded'}</span>
            </div>
        </div>

        <div class="mc-footer">
            Uptime Endpoint: <br>
            <code class="mc-code">GET /trigger?secret={TRIGGER_SECRET if TRIGGER_SECRET else 'YOUR_SECRET'}</code>
        </div>
    </div>

    <script>
        // Server synchronization parameters
        const serverStartMs = {server_epoch_ms};
        const clientStartMs = Date.now();
        const targetHour = {SEND_HOUR};
        const targetMinute = {SEND_MINUTE};
        const triggerSecret = "{TRIGGER_SECRET}";

        let autoRefreshLogs = true;
        let isScrolledUp = false;
        const consoleEl = document.getElementById('mcConsole');

        consoleEl.addEventListener('scroll', () => {{
            const threshold = 30;
            const atBottom = consoleEl.scrollHeight - consoleEl.clientHeight - consoleEl.scrollTop <= threshold;
            isScrolledUp = !atBottom;
        }});

        function getServerNow() {{
            const elapsed = Date.now() - clientStartMs;
            return new Date(serverStartMs + elapsed);
        }}

        function updateCountdown() {{
            const now = getServerNow();

            const pad = (n) => String(n).padStart(2, '0');
            const yr = now.getFullYear();
            const mo = pad(now.getMonth() + 1);
            const da = pad(now.getDate());
            const hr = pad(now.getHours());
            const mi = pad(now.getMinutes());
            const sc = pad(now.getSeconds());
            document.getElementById('serverClock').innerText = `${{yr}}-${{mo}}-${{da}} ${{hr}}:${{mi}}:${{sc}}`;

            const targetToday = new Date(now.getTime());
            targetToday.setHours(targetHour, targetMinute, 0, 0);

            let diffMs = targetToday.getTime() - now.getTime();
            if (diffMs <= 0) {{
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

        // Logs fetching and rendering
        function escapeHtml(str) {{
            if (!str) return '';
            return str
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
        }}

        async function fetchLogs() {{
            try {{
                const res = await fetch('/api/logs?limit=60');
                if (!res.ok) return;
                const data = await res.json();
                const logs = data.logs || [];

                if (logs.length === 0) {{
                    consoleEl.innerHTML = '<div class="log-line" style="color: #666;">No logs recorded yet.</div>';
                    return;
                }}

                const html = logs.map(item => {{
                    const time = item.time || '';
                    const lvl = item.level || 'INFO';
                    const name = item.name || 'app';
                    const msg = item.message || '';
                    const lvlClass = 'log-lvl-' + lvl;
                    return `<div class="log-line">` +
                        `<span class="log-time">[${{time}}]</span> ` +
                        `<span class="${{lvlClass}}">[${{lvl}}]</span> ` +
                        `<span class="log-name">${{name}}:</span> ` +
                        `<span class="log-msg">${{escapeHtml(msg)}}</span>` +
                        `</div>`;
                }}).join('');

                consoleEl.innerHTML = html;

                if (!isScrolledUp) {{
                    consoleEl.scrollTop = consoleEl.scrollHeight;
                }}
            }} catch (e) {{
                // Silent error handling for background polling
            }}
        }}

        function toggleAutoRefresh() {{
            autoRefreshLogs = !autoRefreshLogs;
            const btn = document.getElementById('btnAutoRefresh');
            btn.innerText = autoRefreshLogs ? 'AUTO: ON' : 'AUTO: OFF';
            btn.style.color = autoRefreshLogs ? '#55ff55' : '#aaaaaa';
        }}

        function clearConsoleView() {{
            consoleEl.innerHTML = '<div class="log-line" style="color: #666;">Console view cleared. Incoming logs will appear below.</div>';
        }}

        fetchLogs();
        setInterval(() => {{
            if (autoRefreshLogs) {{
                fetchLogs();
            }}
        }}, 3000);

        // Send Now Action Handler
        async function triggerSendNow() {{
            if (!confirm('Are you sure you want to send all pending Gmail drafts now?')) {{
                return;
            }}

            const btn = document.getElementById('sendBtn');
            const banner = document.getElementById('resultBanner');

            btn.disabled = true;
            btn.innerHTML = '⏳ CONNECTING & SENDING DRAFTS...';
            banner.style.display = 'block';
            banner.className = 'mc-banner info';
            banner.innerText = 'Connecting to Gmail... Check live console below.';

            try {{
                const url = triggerSecret 
                    ? `/trigger?force=true&secret=${{encodeURIComponent(triggerSecret)}}`
                    : `/trigger?force=true`;

                // Trigger sending
                const resPromise = fetch(url);
                
                // Poll logs immediately to show progress
                setTimeout(fetchLogs, 500);
                setTimeout(fetchLogs, 1500);

                const res = await resPromise;
                const data = await res.json();

                // Refresh logs after completion
                fetchLogs();

                if (data.status === 'success') {{
                    const total = data.results?.total_drafts || 0;
                    const sent = data.results?.sent || 0;
                    const failed = data.results?.failed || 0;
                    if (failed > 0 && sent === 0) {{
                        const errMsg = data.results?.errors?.[0]?.error || 'Draft sending failed.';
                        banner.className = 'mc-banner error';
                        banner.innerText = `[FAILED] Sent: ${{sent}}/${{total}}. ${{errMsg}}`;
                    }} else {{
                        banner.className = 'mc-banner success';
                        banner.innerText = `[SUCCESS] Batch Complete! Sent: ${{sent}} / ${{total}} draft(s). Failed: ${{failed}}.`;
                        if (data.date) {{
                            document.getElementById('lastExecDate').innerText = data.date;
                        }}
                    }}
                }} else if (data.status === 'idle') {{
                    banner.className = 'mc-banner info';
                    banner.innerText = `[IDLE] ${{data.message || data.reason || 'No action needed'}}`;
                }} else {{
                    const errMsg = data.error || data.results?.errors?.[0]?.error || data.message || JSON.stringify(data);
                    banner.className = 'mc-banner error';
                    banner.innerText = `[ERROR] ${{errMsg}}`;
                }}
            }} catch (err) {{
                banner.className = 'mc-banner error';
                banner.innerText = `[ERROR] Request failed: ${{err.message}}`;
            }} finally {{
                setTimeout(() => {{
                    btn.disabled = false;
                    btn.innerHTML = '⚡ SEND NOW (INSTANT TRIGGER)';
                    fetchLogs();
                }}, 4000);
            }}
        }}
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html)


@app.get("/api/logs", summary="Recent Server Logs")
def get_logs(limit: int = 60):
    """Returns recent server execution logs for the Minecraft UI terminal."""
    items = list(log_buffer.logs)
    return {"logs": items[-limit:] if limit else items}


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
