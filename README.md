# 🌐 DraftBlaster (Google Chrome & Chromium Edition) 🚀

> **A 100% Client-Side Personal Browser Extension (Manifest V3) for Google Chrome, Opera, Brave, and Microsoft Edge to Automate Sending Gmail Drafts with Human Pacing & Gemini AI Navigation Recovery.**  
> **100% Client-Side • Zero Backend Servers Needed • Safe & Human-Paced**

---

## 🔀 Repository Branch Guide

This repository provides three dedicated solutions for automating Gmail draft sending across different platforms:

| Branch | Platform / Edition | Purpose | When to Use |
|---|---|---|---|
| **`chrome-extension`** *(You are here)* | **Google Chrome & Chromium** | Manifest V3 Extension for Chrome, Opera, Brave, and Edge | Use this branch if you use Chrome, Opera, Brave, or Edge. |
| **[`main`](https://github.com/Gorghs/draftblaster/tree/main)** | **Mozilla Firefox** | Native Firefox Manifest V3 Extension (`.xpi` / Temporary Add-on) | 👉 **Switch to the [`main`](https://github.com/Gorghs/draftblaster/tree/main) branch** for Firefox and Firefox Developer Edition. |
| **[`feature/gmail-api-scheduler`](https://github.com/Gorghs/draftblaster/tree/feature/gmail-api-scheduler)** | **Python / Cloud / Server** | Standalone Python Script using Google Gmail API v1 & OAuth 2.0 | 👉 **Switch to the [`feature/gmail-api-scheduler`](https://github.com/Gorghs/draftblaster/tree/feature/gmail-api-scheduler) branch** for automated headless 9:00 AM cron jobs. |

---

## ⚡ Quick Installation for Google Chrome, Opera, Brave & Edge

### Step 1: Clone the Repository & Build
Open your terminal and run:

```bash
# 1. Clone the repository and switch to the chrome-extension branch
git clone -b chrome-extension https://github.com/Gorghs/draftblaster.git
cd draftblaster

# 2. Install dependencies
npm install

# 3. Build the extension (generates the dist folder)
npm run build
```

*(Once the build finishes, you can close your terminal completely. No server needs to stay running.)*

---

### Step 2: Load into Google Chrome (or Chromium Browser)

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

## 🚦 How to Use DraftBlaster in Chrome

1. Open [Gmail Drafts](https://mail.google.com/#drafts) in Google Chrome.
2. Click the **DraftBlaster 🚀** icon in your browser toolbar.
3. Click the **Gear icon (⚙️)** to open **Settings**:
   - Paste your **Gemini API Key** (get a free key from [Google AI Studio](https://aistudio.google.com/)).
   - Click **Save Settings** (persists securely across Chrome restarts in `chrome.storage.local`).
4. Click **"Scan Drafts"** to automatically list all drafts currently in your Drafts folder.
5. Review the selection and click **"SEND SELECTED"** → **"CONFIRM & SEND"**.
6. DraftBlaster will sequentially open and send each draft with randomized human-like delays (1.5s–4.0s).
7. You can click **STOP** at any time to pause or halt immediately.

---

## 🧪 Safe Testing with "Mock Mode"

Want to test the full UI flow and animations risk-free before sending real emails?

1. Open DraftBlaster → Click **Settings (⚙️)**.
2. Check the box for **"MOCK MODE"** and click **Save Settings**.
3. Click **Scan Drafts** and **SEND SELECTED**.
4. The extension runs with simulated drafts so you can see the state machine in action.
5. Turn **MOCK MODE** off when you are ready to send your real Gmail drafts.

---

## 🛡️ Core Guarantees & Security

- **Drafts Never Change**: Email body, subjects, recipients, CC/BCC, and attachments are 100% preserved and never modified.
- **100% Client-Side**: Operates directly on the Gmail web interface. No servers, no middleware, no telemetry.
- **Local Persistence**: API keys and configurations are saved exclusively to your browser's private local profile (`chrome.storage.local`).
