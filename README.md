# 🦊 DraftBlaster (Firefox Edition) 🚀

<p align="center">
  <img src="public/icons/icon128.png" alt="DraftBlaster Logo" width="128" height="128" />
</p>

<p align="center">
  <strong>The 100% Client-Side Personal Browser Extension to Automate Sending Gmail Drafts in Bulk with Human-Paced Delays & Gemini AI Recovery.</strong>
</p>

<p align="center">
  <a href="https://github.com/Gorghs/draftblaster/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License" /></a>
  <a href="https://github.com/Gorghs/draftblaster/releases"><img src="https://img.shields.io/badge/Version-1.0.1-brightgreen.svg?style=for-the-badge" alt="Version 1.0.1" /></a>
  <a href="https://addons.mozilla.org/"><img src="https://img.shields.io/badge/Firefox-Manifest%20V3-orange.svg?style=for-the-badge&logo=firefox" alt="Firefox MV3" /></a>
  <img src="https://img.shields.io/badge/Backend-Zero%20Servers-success.svg?style=for-the-badge" alt="Zero Backend" />
  <img src="https://img.shields.io/badge/Draft%20Integrity-100%25%20Preserved-purple.svg?style=for-the-badge" alt="Draft Integrity" />
</p>

---

## 🔀 Multi-Platform Repository Branches

DraftBlaster is engineered across three dedicated platform branches:

| Branch | Platform / Edition | Description | Quick Link |
|---|---|---|---|
| **`main`** *(Active)* | **🦊 Mozilla Firefox** | Native Firefox Manifest V3 Extension (`.xpi` installer & source) | [View Firefox Branch](https://github.com/Gorghs/draftblaster/tree/main) |
| **`chrome-extension`** | **🌐 Google Chrome / Chromium** | Manifest V3 Extension for Chrome, Opera, Brave, and Edge | [👉 Go to Chrome Branch](https://github.com/Gorghs/draftblaster/tree/chrome-extension) |
| **`feature/gmail-api-scheduler`** | **🐍 Python / Cloud / Cron** | Headless Python Script using official Gmail API v1 & OAuth 2.0 (9:00 AM Scheduler) | [👉 Go to Python Branch](https://github.com/Gorghs/draftblaster/tree/feature/gmail-api-scheduler) |

---

## 🌟 Why DraftBlaster?

Manually opening and clicking **Send** on dozens of prepared Gmail drafts is slow and tedious. Traditional mass-mailing software requires giving full inbox access to third-party servers.

**DraftBlaster changes that**:
- 🚀 **100% Client-Side Execution**: Runs directly inside your Firefox browser on `mail.google.com`.
- 🛡️ **Strict Draft Integrity**: Body text, subjects, recipients, CC/BCC, and attachments are **never modified or altered**.
- ⏱️ **Natural Human Pacing**: Sends each draft with randomized 1.5s–4.0s delays to keep your Google account completely safe.
- 🛑 **Emergency Stop**: One-click instant halt at any second during a batch run.
- 🤖 **Gemini Navigation Recovery**: Uses Google's Gemini AI purely as a navigation fallback if unexpected UI popups block the view.

---

## ⚡ Quick Installation (Firefox)

### Method 1: Permanent File Install (`.xpi`) in Firefox Developer Edition
*(Recommended for permanent everyday use)*

1. Enable unsigned add-on file loading:
   - Type **`about:config`** in Firefox address bar and press Enter.
   - Search for **`xpinstall.signatures.required`** and toggle it to **`false`**.
2. Open Add-ons Manager: **`about:addons`** (or press `Ctrl + Shift + A`).
3. Click the **Gear icon (⚙️)** in top right → **"Install Add-on From File..."**.
4. Select the pre-built [**`draftblaster.xpi`**](file:///home/karthick/Projects/draftblaster/draftblaster.xpi) archive from this repository.
5. Click **"Add"** to install permanently.

---

### Method 2: Load as Temporary Add-on (Standard Firefox)

1. Open Firefox and go to:
   ```
   about:debugging#/runtime/this-firefox
   ```
2. Click **"Load Temporary Add-on..."**.
3. Select `draftblaster.xpi` or `dist/manifest.json`.
4. DraftBlaster icon 🚀 will appear in your Firefox toolbar.

---

## 🛠️ Build from Source

```bash
# 1. Clone repository
git clone https://github.com/Gorghs/draftblaster.git
cd draftblaster

# 2. Install dependencies
npm install

# 3. Build & package Firefox .xpi
npm run build:xpi
```

---

## 🚦 Step-by-Step Usage Guide

1. Open [Gmail Drafts](https://mail.google.com/#drafts) in Firefox.
2. Click the **DraftBlaster 🚀** icon in your toolbar.
3. Open **Settings (⚙️)**:
   - Paste your free **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).
   - Click **Save Settings** (persists locally in browser storage).
4. Click **"Scan Drafts"** to list all available drafts.
5. Review draft list, select which drafts to send, and click **"SEND SELECTED"** → **"CONFIRM & SEND"**.
6. DraftBlaster will send your emails one-by-one with human-paced delays.

---

## 🔒 Security & Privacy Architecture

- **Zero Cloud Proxies**: Operates strictly within Firefox's local extension sandbox.
- **Local Secret Storage**: API keys are saved exclusively in `browser.storage.local`.
- **Encrypted Header Authentication**: Gemini requests transmit keys via secure `x-goog-api-key` TLS request headers.
- **Read our complete [Security Policy](SECURITY.md)**.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
