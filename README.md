# DraftBlaster 🚀

> **A 100% Client-Side, Zero-Backend Personal Browser Extension (Manifest V3) for Automating Gmail Draft Sending**  
> Supported Browsers: **Google Chrome**, **Opera**, **Brave**, **Microsoft Edge**, and **Mozilla Firefox**.

---

## ⚡ Quick Start (Load directly into Chrome / Opera / Brave)

If `dist/` is already built:
1. Open your browser and go to `chrome://extensions` (or `opera://extensions` / `brave://extensions`).
2. Turn on the **Developer mode** toggle (top-right corner).
3. Click **Load unpacked** (top-left) and select the `dist/` folder.
4. Open [Gmail Drafts](https://mail.google.com/#drafts), click the **DraftBlaster** toolbar icon, open **Settings (⚙️)**, and paste your **Gemini API Key**. Done!

---

## 📑 Table of Contents
- [Why DraftBlaster?](#-why-draftblaster)
- [🔒 100% Client-Side Architecture (No Backend Needed)](#-100-client-side-architecture-no-backend-needed)
- [🛡️ Draft Integrity Guarantee (Drafts Never Change)](#️-draft-integrity-guarantee-drafts-never-change)
- [📦 Building from Source (Developers)](#-building-from-source-developers)
- [🚦 Complete Step-by-Step Usage Guide](#-complete-step-by-step-usage-guide)
- [⚙️ Settings & Configuration](#️-settings--configuration)
- [🤖 How Gemini AI Navigation Recovery Works](#-how-gemini-ai-navigation-recovery-works)
- [🧪 Running Automated Tests](#-running-automated-tests)
- [🔐 Security & Privacy](#-security--privacy)

---

## 💡 Why DraftBlaster?

When managing bulk outreach, newsletters, or follow-ups, users often prepare dozens or hundreds of drafts in Gmail and need to click "Send" on each one individually. 

**DraftBlaster** automates this tedious process directly from your browser. It scans your existing Gmail drafts, verifies safety criteria, lets you review and select which drafts to send, and sends them one by one with customizable, human-like delays—all without running any external servers or background scripts.

---

## 🔒 100% Client-Side Architecture (No Backend Needed)

DraftBlaster is completely self-contained within your browser. There is **no backend server**, **no middleware**, and **no external database** required.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                             YOUR BROWSER                                 │
│                                                                          │
│  ┌──────────────────────┐              ┌──────────────────────────────┐  │
│  │   DraftBlaster UI    │ ───────────> │ Gmail Web Tab                │  │
│  │   (Popup / React)    │  DOM Events  │ (mail.google.com/#drafts)    │  │
│  └──────────┬───────────┘              └──────────────────────────────┘  │
│             │                                         │                  │
│             │ (Only during UI recovery)               │ Direct Sending   │
│             ▼                                         ▼                  │
│  ┌──────────────────────┐              ┌──────────────────────────────┐  │
│  │ Google Gemini API    │              │ Google Mail Delivery         │  │
│  │ (Direct HTTPS Call)  │              │ (Native Gmail Infrastructure)│  │
│  └──────────────────────┘              └──────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

- **Zero Backend Servers**: No Node.js, Express, Python, or Docker instances to host or run.
- **Zero Cloud Databases**: No Firestore, Supabase, or SQL databases. Everything lives in `chrome.storage.local`.
- **Zero Gmail API / OAuth Setup**: Operates directly on the rendered Gmail web page using safe DOM automation. You don't need Google Cloud Console OAuth verification.
- **Direct Gemini Client**: Navigation recovery requests are sent directly from your browser to Google's Gemini endpoint via client-side HTTPS.

---

## 🛡️ Draft Integrity Guarantee (Drafts Never Change)

DraftBlaster follows a strict **zero-modification principle**:

1. **Draft Content is Never Altered**: The subject line, email body, recipient list, CC/BCC, and attachments remain 100% intact exactly as you composed them in Gmail.
2. **Read-and-Send Only**: The extension only reads metadata (recipient, subject snippet) to display in the extension UI, opens the draft window, verifies that it matches, and triggers the native Gmail Send button.
3. **No Injected Tracking / Footers**: No extra text, signatures, or tracking pixels are ever added to your emails.

---

## 📦 Building from Source (Developers)

If you clone the repository to a new machine or modify the TypeScript/React code:

### 1. Install Dependencies & Build
```bash
# 1. Install build tools and dependencies (Vite, React, TypeScript)
npm install

# 2. Compile static extension into dist/
npm run build
```

> **Why `npm install`?**  
> GitHub repositories do not store third-party packages (`node_modules`). `npm install` is only needed when building from source code to download Vite and React for compilation.

### 2. (Optional) Configure Default Environment Variables
You can optionally bake a default API key into the build using `.env` (or just paste it into the UI after loading):
```bash
cp .env.example .env
```
Edit `.env`:
```env
VITE_GEMINI_API_KEY=your_gemini_api_key_here
VITE_GEMINI_MODEL=gemini-2.5-flash
```

---

## 🚦 Complete Step-by-Step Usage Guide

### Phase 1: Prepare Your Drafts in Gmail
1. Log into your standard Gmail account at [mail.google.com](https://mail.google.com).
2. Create your email drafts normally. Fill in the recipients, subjects, body copy, and any attachments.
3. Navigate to your **Drafts** view ([mail.google.com/#drafts](https://mail.google.com/#drafts)).

### Phase 2: Scan Drafts
1. Click the **DraftBlaster** extension icon in your browser toolbar to open the popup.
2. Click the **Scan Drafts** button.
3. DraftBlaster reads the active Gmail Drafts list and displays:
   - Recipient email address.
   - Subject line preview.
   - Total draft count.

### Phase 3: Review and Select
1. By default, all scanned drafts up to your configured Run Limit (e.g. 500) are selected.
2. You can uncheck any individual drafts you wish to skip.

### Phase 4: Confirmation & Safe Sending
1. Click the **SEND SELECTED** button.
2. A confirmation modal will appear displaying:
   - Total number of selected drafts.
   - Pacing parameters (e.g., 1.5s – 4.0s randomized delay per email).
   - Recipient verification status.
3. Click **CONFIRM & SEND**.
4. DraftBlaster will sequentially:
   - Open each draft.
   - Perform safety checks (ensuring valid recipient and compose window presence).
   - Click the native Gmail Send button.
   - Apply a randomized human-like delay before proceeding to the next draft.
5. **Emergency Stop**: You can click the **STOP** button at any time during the run to immediately halt sending.

---

## ⚙️ Settings & Configuration

Click the **Gear Icon (⚙️)** in the DraftBlaster popup to customize options:

| Setting | Default | Description |
|---|---|---|
| **Gemini API Key** | Empty / Stored locally | Your Google Gemini API key used for UI navigation recovery. Paste it directly in this field and click Save. |
| **Gemini Model** | `gemini-2.5-flash` | The Gemini model name used for vision/navigation assistance. |
| **Run Limit** | `500` | Maximum number of drafts to process in a single automated batch. |
| **Min Delay (ms)** | `1500` | Minimum wait time between sends (in milliseconds) to prevent rate limiting. |
| **Max Delay (ms)** | `4000` | Maximum wait time between sends to maintain human-like interaction pacing. |
| **Mock Mode** | `Off` | Simulates the entire scanning and sending workflow without actually clicking Send or modifying Gmail. Useful for testing UI and flows risk-free. |

---

## 🤖 How Gemini AI Navigation Recovery Works

If Gmail's user interface updates, or if a modal, prompt, or overlay temporarily blocks the Drafts view:
1. DraftBlaster captures a snapshot of the interface state.
2. It sends a structured analysis prompt to the Gemini API over client-side HTTPS.
3. Gemini determines the appropriate navigation action (e.g., dismissing an overlay, returning to `#drafts`).
4. **Strict Safety Boundary**: AI recommendations are strictly restricted to navigation/recovery actions (`OPEN_DRAFTS`, `DISMISS_MODAL`). The AI is cryptographically and logically forbidden from ever triggering the `SEND` action directly.

---

## 🧪 Running Automated Tests

DraftBlaster includes comprehensive unit tests and safety assertion suites using Vitest:

```bash
npm test
```

---

## 🔐 Security & Privacy

- **Your Emails Remain Private**: Email content never leaves your browser. Content is only rendered by Gmail and transmitted directly through Google Mail servers.
- **Local Storage Only**: API keys and preferences are stored exclusively on your device via `chrome.storage.local`.
- **No Third-Party Analytics**: No telemetry, analytics trackers, or external logging.
