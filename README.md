# 🌐 DraftBlaster (Google Chrome & Chromium Edition) 🚀

<p align="center">
  <img src="public/icons/icon128.png" alt="DraftBlaster Logo" width="128" height="128" />
</p>

<p align="center">
  <strong>The 100% Client-Side Manifest V3 Browser Extension for Google Chrome, Opera, Brave, and Edge to Automate Sending Gmail Drafts in Bulk with Human-Paced Delays & Gemini AI Recovery.</strong>
</p>

<p align="center">
  <a href="https://github.com/Gorghs/draftblaster/blob/chrome-extension/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License" /></a>
  <a href="https://github.com/Gorghs/draftblaster/releases"><img src="https://img.shields.io/badge/Version-1.0.1-brightgreen.svg?style=for-the-badge" alt="Version 1.0.1" /></a>
  <a href="https://developer.chrome.com/docs/extensions/mv3/intro/"><img src="https://img.shields.io/badge/Chrome-Manifest%20V3-yellow.svg?style=for-the-badge&logo=googlechrome" alt="Chrome MV3" /></a>
  <img src="https://img.shields.io/badge/Backend-Zero%20Servers-success.svg?style=for-the-badge" alt="Zero Backend" />
  <img src="https://img.shields.io/badge/Draft%20Integrity-100%25%20Preserved-purple.svg?style=for-the-badge" alt="Draft Integrity" />
</p>

---

## 🔀 Multi-Platform Repository Branches

DraftBlaster is engineered across three dedicated platform branches:

| Branch | Platform / Edition | Description | Quick Link |
|---|---|---|---|
| **`chrome-extension`** *(Active)* | **🌐 Google Chrome / Chromium** | Manifest V3 Extension for Chrome, Opera, Brave, and Edge | [View Chrome Branch](https://github.com/Gorghs/draftblaster/tree/chrome-extension) |
| **[`main`](https://github.com/Gorghs/draftblaster/tree/main)** | **🦊 Mozilla Firefox** | Native Firefox Manifest V3 Extension (`.xpi` installer & source) | [👉 Go to Firefox Branch](https://github.com/Gorghs/draftblaster/tree/main) |
| **[`feature/gmail-api-scheduler`](https://github.com/Gorghs/draftblaster/tree/feature/gmail-api-scheduler)** | **🐍 Python / Cloud / Cron** | Headless Python Script using official Gmail API v1 & OAuth 2.0 (9:00 AM Scheduler) | [👉 Go to Python Branch](https://github.com/Gorghs/draftblaster/tree/feature/gmail-api-scheduler) |

---

## 🌟 Why DraftBlaster?

Manually opening and clicking **Send** on dozens of prepared Gmail drafts is slow and tedious. Traditional mass-mailing software requires giving full inbox access to third-party servers.

**DraftBlaster changes that**:
- 🚀 **100% Client-Side Execution**: Runs directly inside your Google Chrome / Chromium browser on `mail.google.com`.
- 🛡️ **Strict Draft Integrity**: Body text, subjects, recipients, CC/BCC, and attachments are **never modified or altered**.
- ⏱️ **Natural Human Pacing**: Sends each draft with randomized 1.5s–4.0s delays to keep your Google account completely safe.
- 🛑 **Emergency Stop**: One-click instant halt at any second during a batch run.
- 🤖 **Gemini Navigation Recovery**: Uses Google's Gemini AI purely as a navigation fallback if unexpected UI popups block the view.

---

## ⚡ Quick Installation (Google Chrome / Opera / Brave / Edge)

### Step 1: Clone & Build

```bash
# 1. Clone this branch
git clone -b chrome-extension https://github.com/Gorghs/draftblaster.git
cd draftblaster

# 2. Install dependencies
npm install

# 3. Build static extension bundle
npm run build
```

*(Once the build finishes, you can close your terminal completely. No server needs to stay running.)*

---

### Step 2: Load into Chrome / Chromium

1. Open **Google Chrome** and navigate to:
   ```
   chrome://extensions
   ```
   *(For **Opera**, open `opera://extensions` • For **Brave**, open `brave://extensions` • For **Edge**, open `edge://extensions`)*
2. In the top-right corner, turn **ON** the **Developer mode** toggle switch.
3. In the top-left corner, click the **"Load unpacked"** button.
4. In the file picker window, select the **`dist`** folder inside your `draftblaster` project folder:
   ```
   /path/to/draftblaster/dist
   ```
5. Click **Select / Open**.
6. Click the **Extensions puzzle piece icon** in Chrome's top toolbar and click the **Pin 📌** icon next to DraftBlaster.

---

## 🚦 Step-by-Step Usage Guide

1. Open [Gmail Drafts](https://mail.google.com/#drafts) in Google Chrome.
2. Click the **DraftBlaster 🚀** icon in your toolbar.
3. Open **Settings (⚙️)**:
   - Paste your free **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).
   - Click **Save Settings** (persists locally in browser storage).
4. Click **"Scan Drafts"** to list all available drafts.
5. Review draft list, select which drafts to send, and click **"SEND SELECTED"** → **"CONFIRM & SEND"**.
6. DraftBlaster will send your emails one-by-one with human-paced delays.

---

## 🔒 Security & Privacy Architecture

- **Zero Cloud Proxies**: Operates strictly within Chrome's local extension sandbox.
- **Local Secret Storage**: API keys are saved exclusively in `chrome.storage.local`.
- **Encrypted Header Authentication**: Gemini requests transmit keys via secure `x-goog-api-key` TLS request headers.
- **Read our complete [Security Policy](SECURITY.md)**.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
