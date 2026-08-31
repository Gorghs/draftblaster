# 🦊 DraftBlaster (Firefox Edition) 🚀

> **A 100% Client-Side Personal Browser Extension for Mozilla Firefox & Firefox Developer Edition to Automate Sending Gmail Drafts with Human Pacing & Gemini Recovery.**  
> **100% Client-Side • Zero Backend Servers • Direct XPI Installation**

---

## 🔀 Repository Branch Guide

This repository provides three dedicated solutions for automating Gmail draft sending across different platforms:

| Branch | Platform / Edition | Purpose | When to Use |
|---|---|---|---|
| **`main`** *(You are here)* | **Mozilla Firefox** | Native Firefox Manifest V3 Extension (`.xpi` / Temporary Add-on) | Use this branch if you are running Firefox or Firefox Developer Edition. |
| **[`chrome-extension`](https://github.com/Gorghs/draftblaster/tree/chrome-extension)** | **Google Chrome & Chromium** | Manifest V3 Extension for Chrome, Opera, Brave, and Edge | 👉 **Switch to the [`chrome-extension`](https://github.com/Gorghs/draftblaster/tree/chrome-extension) branch** if you use Chrome, Brave, or Opera. |
| **[`feature/gmail-api-scheduler`](https://github.com/Gorghs/draftblaster/tree/feature/gmail-api-scheduler)** | **Python / Cloud / Server** | Standalone Python Script using Google Gmail API v1 & OAuth 2.0 | 👉 **Switch to the [`feature/gmail-api-scheduler`](https://github.com/Gorghs/draftblaster/tree/feature/gmail-api-scheduler) branch** for automated headless 9:00 AM cron jobs. |

---

## ⚡ Quick Installation for Firefox (2 Methods)

### Method 1: Permanent File Install (`.xpi`) in Firefox Developer Edition
*(Recommended for daily use without needing to reload)*

1. In Firefox Developer Edition, enable unsigned extension file loading:
   - Type **`about:config`** in the address bar and press Enter.
   - Search for **`xpinstall.signatures.required`** and toggle it to **`false`**.
2. Open Add-ons Manager: **`about:addons`** (or press `Ctrl + Shift + A`).
3. Click the **Gear icon (⚙️)** in the top right → **"Install Add-on From File..."**.
4. Select the pre-packaged **`draftblaster.xpi`** from this repository.
5. Click **"Add"** to install.

---

### Method 2: Load as Temporary Add-on (Standard Firefox)

1. Open Firefox and navigate to:
   ```
   about:debugging#/runtime/this-firefox
   ```
2. Click **"Load Temporary Add-on..."**.
3. Select either `draftblaster.xpi` or the `dist/manifest.json` file.
4. DraftBlaster will appear in your Firefox toolbar.

---

## 🛠️ Building from Source

If you clone or modify the source code:

```bash
# 1. Install dependencies
npm install

# 2. Compile and package the fresh .xpi archive
npm run build:xpi
```

This compiles TypeScript and packages a ready-to-install `draftblaster.xpi` archive in the root directory.

---

## 🚦 How to Use DraftBlaster in Firefox

1. Open [Gmail Drafts](https://mail.google.com/#drafts) in Firefox.
2. Click the **DraftBlaster 🚀** icon in your Firefox toolbar.
3. Click the **Settings icon (⚙️)**:
   - Paste your **Gemini API Key** (get a free key from [Google AI Studio](https://aistudio.google.com/)).
   - Click **Save Settings** (persists locally in Firefox storage).
4. Click **"Scan Drafts"** to list all available drafts.
5. Select the drafts you want to send and click **"SEND SELECTED"** → **"CONFIRM & SEND"**.
6. DraftBlaster sends each draft one-by-one with randomized human-like delays (1.5s–4.0s).
7. You can click **STOP** at any time to pause immediately.

---

## 🧪 Safe Testing with "Mock Mode"

Want to test the interface and sending animations without actually sending real emails?

1. Open DraftBlaster → Click **Settings (⚙️)**.
2. Check the box for **"MOCK MODE"** and click **Save Settings**.
3. Click **Scan Drafts** and **SEND SELECTED**.
4. DraftBlaster will simulate the complete workflow risk-free.
5. Uncheck Mock Mode in Settings when you are ready for real sending.

---

## 🛡️ Core Guarantees

- **Drafts Never Change**: Email body, subjects, recipients, CC/BCC, and attachments are never modified.
- **100% Client-Side**: No backend servers, no cloud databases, zero external tracking.
- **Persistent Storage**: API keys and settings survive browser restarts in `browser.storage.local`.
