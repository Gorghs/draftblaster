"""
OAuth 2.0 Web Flow Routes for one-time Google authorization.
Supports both /auth/login, /oauth/login and /auth/callback, /oauth/callback.
"""

import logging
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from google_auth_oauthlib.flow import Flow

from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    OAUTH_REDIRECT_URI,
    GMAIL_SCOPE
)

logger = logging.getLogger("oauth_routes")
router = APIRouter(tags=["Google OAuth"])


def get_effective_redirect_uri(request: Request) -> str:
    """Dynamically determines the redirect URI matching the request and config."""
    if OAUTH_REDIRECT_URI and "localhost" not in OAUTH_REDIRECT_URI:
        return OAUTH_REDIRECT_URI

    # If running on Render, construct from current host
    host = request.base_url.hostname or "localhost"
    path = "/oauth/callback" if "oauth" in request.url.path else "/auth/callback"
    scheme = "https" if "onrender.com" in host or request.url.scheme == "https" else "http"
    port_str = f":{request.base_url.port}" if request.base_url.port and scheme == "http" else ""
    return f"{scheme}://{host}{port_str}{path}"


def create_oauth_flow(redirect_uri: str) -> Flow:
    """Initializes Google OAuth Flow from client credentials."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be configured in environment variables."
        )

    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=[GMAIL_SCOPE],
        redirect_uri=redirect_uri
    )
    return flow


@router.get("/auth/login", summary="Initiate Google OAuth 2.0 Authorization (/auth/login)")
@router.get("/oauth/login", summary="Initiate Google OAuth 2.0 Authorization (/oauth/login)")
def auth_login(request: Request):
    """
    Generates the Google OAuth authorization URL requesting offline access
    and prompt=consent so a refresh token is guaranteed to be returned.
    """
    redirect_uri = get_effective_redirect_uri(request)
    flow = create_oauth_flow(redirect_uri)
    
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true"
    )

    logger.info("Generated OAuth authorization URL for redirect_uri: %s", redirect_uri)
    return RedirectResponse(authorization_url)


@router.get("/auth/callback", summary="Handle Google OAuth 2.0 Callback (/auth/callback)")
@router.get("/oauth/callback", summary="Handle Google OAuth 2.0 Callback (/oauth/callback)")
def auth_callback(request: Request, code: str = None, error: str = None):
    """
    Exchanges authorization code for tokens, extracts the refresh token,
    and displays instructions for setting it in Render environment variables.
    """
    if error:
        logger.warning("OAuth authorization error received: %s", error)
        return HTMLResponse(
            content=f"""
            <html>
                <body style="font-family: sans-serif; padding: 40px; background: #0f172a; color: #f8fafc;">
                    <div style="max-width: 600px; margin: auto; background: #1e293b; padding: 24px; border-radius: 12px; border: 1px solid #ef4444;">
                        <h2 style="color: #ef4444;">❌ Google Authorization Denied</h2>
                        <p>Google returned an error: <code>{error}</code></p>
                        <a href="/auth/login" style="display: inline-block; margin-top: 16px; padding: 10px 20px; background: #38bdf8; color: #0f172a; border-radius: 6px; text-decoration: none; font-weight: bold;">Try Again</a>
                    </div>
                </body>
            </html>
            """,
            status_code=400
        )

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    redirect_uri = get_effective_redirect_uri(request)

    try:
        flow = create_oauth_flow(redirect_uri)
        # Exchange code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials

        refresh_token = credentials.refresh_token

        if not refresh_token:
            logger.warning("No refresh token returned by Google (access token only).")
            return HTMLResponse(
                content="""
                <html>
                    <body style="font-family: sans-serif; padding: 40px; background: #0f172a; color: #f8fafc;">
                        <div style="max-width: 650px; margin: auto; background: #1e293b; padding: 28px; border-radius: 12px; border: 1px solid #f59e0b;">
                            <h2 style="color: #f59e0b;">⚠️ No Refresh Token Returned</h2>
                            <p>Google only returned an access token because your Google account has authorized this application previously without revoking consent.</p>
                            <p>Please revoke access at <a href="https://myaccount.google.com/permissions" target="_blank" style="color: #38bdf8;">Google Account Permissions</a> and click below to re-authorize with full consent.</p>
                            <a href="/auth/login" style="display: inline-block; margin-top: 16px; padding: 10px 20px; background: #38bdf8; color: #0f172a; border-radius: 6px; text-decoration: none; font-weight: bold;">Force Consent Re-Login</a>
                        </div>
                    </body>
                </html>
                """,
                status_code=200
            )

        # Do NOT log the refresh token in server logs for security!
        logger.info("Successfully obtained Google OAuth refresh token.")

        # Display clean HTML for user to copy into Render Environment Variables
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DraftBlaster OAuth Complete</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    background-color: #0b1120;
                    color: #f8fafc;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    padding: 20px;
                    box-sizing: border-box;
                }}
                .card {{
                    background: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 14px;
                    padding: 32px;
                    max-width: 680px;
                    width: 100%;
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
                }}
                h1 {{
                    margin-top: 0;
                    color: #38bdf8;
                    font-size: 22px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .token-box {{
                    background: #0f172a;
                    border: 1px solid #475569;
                    padding: 14px;
                    border-radius: 8px;
                    font-family: monospace;
                    font-size: 13px;
                    word-break: break-all;
                    margin: 16px 0;
                    color: #a5f3fc;
                    user-select: all;
                }}
                .btn {{
                    background: #0284c7;
                    color: white;
                    border: none;
                    padding: 10px 18px;
                    border-radius: 6px;
                    font-weight: 600;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    transition: background 0.15s;
                }}
                .btn:hover {{
                    background: #0369a1;
                }}
                .step-list {{
                    background: #0f172a;
                    padding: 16px 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #cbd5e1;
                }}
                .step-list ol {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .step-list li {{
                    margin-bottom: 8px;
                }}
                .badge {{
                    background: #166534;
                    color: #bbf7d0;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>✅ Google Authorization Successful! <span class="badge">One-Time Setup</span></h1>
                <p style="color: #94a3b8; font-size: 14px;">
                    Your long-lived OAuth 2.0 Refresh Token has been generated. This token enables unattended, automated Gmail draft sending without repeated logins.
                </p>

                <label style="font-weight: 600; font-size: 13px; color: #cbd5e1;">Your GOOGLE_REFRESH_TOKEN:</label>
                <div class="token-box" id="tokenBox">{refresh_token}</div>
                
                <button class="btn" onclick="copyToken()">📋 Copy Refresh Token</button>
                <span id="copyNotice" style="margin-left: 12px; color: #4ade80; font-size: 13px; display: none;">Copied to clipboard!</span>

                <div class="step-list">
                    <strong>Final Setup Steps:</strong>
                    <ol>
                        <li>Copy the token above.</li>
                        <li>Open your <strong>Render Dashboard</strong> → Your Web Service → <strong>Environment</strong>.</li>
                        <li>Add/Update the environment variable: <code>GOOGLE_REFRESH_TOKEN</code> with this copied value.</li>
                        <li>Save changes. Render will automatically redeploy with unattended automation enabled!</li>
                        <li>Configure your external uptime service to ping <code>/trigger?secret=YOUR_SECRET</code> every minute.</li>
                    </ol>
                </div>
            </div>

            <script>
                function copyToken() {{
                    const text = document.getElementById('tokenBox').innerText;
                    navigator.clipboard.writeText(text).then(() => {{
                        const notice = document.getElementById('copyNotice');
                        notice.style.display = 'inline';
                        setTimeout(() => {{ notice.style.display = 'none'; }}, 3000);
                    }});
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)

    except Exception as e:
        logger.error("OAuth token exchange failed: %s", e)
        return HTMLResponse(
            content=f"""
            <html>
                <body style="font-family: sans-serif; padding: 40px; background: #0f172a; color: #f8fafc;">
                    <div style="max-width: 600px; margin: auto; background: #1e293b; padding: 24px; border-radius: 12px; border: 1px solid #ef4444;">
                        <h2 style="color: #ef4444;">❌ Token Exchange Failed</h2>
                        <p>{str(e)}</p>
                        <a href="/auth/login" style="display: inline-block; margin-top: 16px; padding: 10px 20px; background: #38bdf8; color: #0f172a; border-radius: 6px; text-decoration: none; font-weight: bold;">Retry Authorization</a>
                    </div>
                </body>
            </html>
            """,
            status_code=500
        )
