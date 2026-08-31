# 🔒 Security Policy & Data Integrity Guarantee

DraftBlaster is engineered with a **zero-trust, strict client-side architecture** to guarantee the privacy, security, and integrity of your email data.

---

## 🛡️ Core Security Architecture

### 1. 100% Client-Side Sandbox (Browser Extensions)
- **Zero Backend Servers**: No intermediary servers, databases, or cloud proxies handle your emails.
- **Direct Native Execution**: Content scripts operate directly within your active Gmail web session (`mail.google.com`).
- **No Third-Party Analytics**: No trackers, telemetry, or user behavior tracking of any kind.
- **Local Secret Storage**: All API keys and preferences are stored exclusively in your browser's sandboxed storage (`chrome.storage.local` / `browser.storage.local`).

### 2. Zero-Modification Draft Integrity Guarantee
- **Read & Send Only**: DraftBlaster never modifies, edits, injects into, or deletes your drafts.
- **Preserved Email Metadata**: Email bodies, subject lines, recipients, CC/BCC, and attachments remain 100% untouched.

### 3. AI Safety Boundary (Gemini Navigation Recovery)
- **Restricted Scope**: Google Gemini AI is used **strictly for UI navigation state analysis** when Gmail displays unexpected overlays or dialogs.
- **Cryptographic & Logic Lockout**: The state machine strictly forbids AI models from executing or triggering the `SEND` action. Only the deterministic, user-confirmed engine can initiate sending.
- **Encrypted Header Auth**: API keys are transmitted via `x-goog-api-key` TLS request headers rather than URL query parameters.

### 4. Headless Python OAuth 2.0 Security
- **Official Google APIs**: Uses the official Google Gmail API v1 with standard OAuth 2.0 PKCE / Installed App flow.
- **Token Protection**: Access and refresh tokens are stored locally in `token.json` and excluded from source control via `.gitignore`.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability or potential data leak within DraftBlaster, please report it privately:

- **Email**: `dev.karthickv@gmail.com`
- **Response Time**: Initial acknowledgment within 24 hours.

Please include:
1. Description of the vulnerability and its potential impact.
2. Step-by-step reproduction instructions or proof-of-concept.
3. Affected browser / platform environment.

---

## 📜 Supported Versions

| Version | Supported | Security Updates |
|---|---|---|
| `1.0.x` (Latest) | :white_check_mark: | Active |
| `< 1.0.0` | :x: | End of Life |
