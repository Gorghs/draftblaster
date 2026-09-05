"""
FastAPI application entrypoint for Gmail Draft Auto-Sender.
Supports both Gmail App Password (IMAP/SMTP) and Google OAuth 2.0.
"""

import os
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Security, status, Header, Query
from fastapi.responses import JSONResponse, HTMLResponse

from config import (
    PORT,
    HOST,
    TIMEZONE_STR,
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
    version="2.2.0",
    lifespan=lifespan
)

# Mount OAuth routes (/oauth/login, /auth/login, /oauth/callback, /auth/callback)
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
    """Renders a friendly web UI showing service status and configuration."""
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

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gmail Draft Auto-Sender</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: #0f172a;
                color: #f8fafc;
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
            }}
            .container {{
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 28px;
                max-width: 650px;
                width: 100%;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            }}
            h1 {{ color: #38bdf8; margin-top: 0; font-size: 24px; }}
            .item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #334155; font-size: 14px; }}
            .item:last-child {{ border-bottom: none; }}
            .label {{ color: #94a3b8; font-weight: 500; }}
            .value {{ font-family: monospace; color: #f1f5f9; }}
            .badge {{ background: #166534; color: #bbf7d0; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Gmail Draft Auto-Sender</h1>
            <p style="color: #cbd5e1; font-size: 14px;">Automated background service on Render triggered every minute by external uptime ping.</p>
            
            <div style="margin: 20px 0;">
                <div class="item"><span class="label">Status:</span><span class="value"><span class="badge">Active</span></span></div>
                <div class="item"><span class="label">Auth Method:</span><span class="value">{auth_mode}</span></div>
                <div class="item"><span class="label">Auth Status:</span><span class="value">{auth_status}</span></div>
                <div class="item"><span class="label">Configured Timezone:</span><span class="value">{TIMEZONE_STR}</span></div>
                <div class="item"><span class="label">Current Server Time:</span><span class="value">{now.strftime('%Y-%m-%d %H:%M:%S')}</span></div>
                <div class="item"><span class="label">Scheduled Send Time:</span><span class="value">{SEND_HOUR:02d}:{SEND_MINUTE:02d} ({TIMEZONE_STR})</span></div>
                <div class="item"><span class="label">Last Executed Date:</span><span class="value">{last_run.get('last_send_date') or 'None recorded'}</span></div>
            </div>

            <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #334155; font-size: 12px; color: #64748b;">
                Endpoint: <code>GET /trigger?secret=YOUR_SECRET</code> (Ping every 1 minute)
            </div>
        </div>
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
