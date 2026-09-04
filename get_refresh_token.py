#!/usr/bin/env python3
"""
One-time CLI tool to obtain Google OAuth 2.0 Refresh Token locally.
"""

import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or os.getenv("GMAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET") or os.getenv("GMAIL_CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET missing in .env")
        return

    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }

    try:
        flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
        print("\nOpening browser for Google Authorization...")
        print("If prompt appears, click 'Advanced' -> 'Go to (unsafe)' and grant permission.\n")
        creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
        
        if creds.refresh_token:
            print("=" * 60)
            print("SUCCESS! Here is your GOOGLE_REFRESH_TOKEN:")
            print("=" * 60)
            print(creds.refresh_token)
            print("=" * 60)
            print("\nSave this as GOOGLE_REFRESH_TOKEN in your .env and on Render!")
            
            # Append to local .env if not present
            with open(".env", "a", encoding="utf-8") as f:
                f.write(f"\nGOOGLE_REFRESH_TOKEN={creds.refresh_token}\n")
            print("Appended GOOGLE_REFRESH_TOKEN to your local .env file.")
        else:
            print("WARNING: No refresh token returned. Go to https://myaccount.google.com/permissions to revoke app access and retry.")
    except Exception as e:
        print(f"Error during authorization: {e}")

if __name__ == "__main__":
    main()
