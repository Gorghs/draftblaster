# 🚀 DraftBlaster

> **Automate sending your Gmail drafts in bulk directly from your browser.**  
> **100% Client-Side • Zero Backend Servers • Safe & Human-Paced**

---

## 📖 Table of Contents
1. [What is DraftBlaster?](#-what-is-draftblaster)
2. [How Does it Work? (100% Client-Side)](#-how-does-it-work-100-client-side)
3. [Beginner Quick Start Guide](#-beginner-quick-start-guide)
   - [Step 1: Get Your Free Gemini API Key](#step-1-get-your-free-gemini-api-key)
   - [Step 2: Prepare the Extension Files (One-Time Build)](#step-2-prepare-the-extension-files-one-time-build)
   - [Step 3: Load the Extension into Google Chrome](#step-3-load-the-extension-into-google-chrome)
   - [Step 4: Load into Other Browsers (Opera, Brave, Edge, Firefox)](#step-4-load-into-other-browsers)
4. [Step-by-Step Usage Guide (How to Send Drafts)](#-step-by-step-usage-guide)
5. [Practicing Safely with "Mock Mode"](#-practicing-safely-with-mock-mode)
6. [Settings & Customization](#-settings--customization)
7. [Frequently Asked Questions (FAQ) & Troubleshooting](#-frequently-asked-questions-faq--troubleshooting)

---

## 💡 What is DraftBlaster?

If you frequently write multiple email drafts in Gmail (for follow-ups, outreach, newsletters, or notifications), clicking into each draft and pressing "Send" one by one is repetitive and time-consuming.

**DraftBlaster** is a browser extension that:
- 🔍 **Scans all your ready drafts** in your Gmail Drafts folder.
- 📋 **Lists them cleanly** so you can choose which ones to send.
- ⏱️ **Sends them one-by-one automatically** with natural, randomized delays (1.5 to 4 seconds) so Gmail never flags your account as a spam bot.
- 🛡️ **Guarantees Draft Integrity**: Your email bodies, subjects, recipients, and attachments are **never modified**. DraftBlaster sends them exactly as you wrote them.
- 🛑 **Instant STOP button**: Pause or cancel sending at any moment with one click.

---

## 🔒 How Does it Work? (100% Client-Side)

### Do I need a backend server running?
**No! You do NOT need any server or terminal running while using DraftBlaster.**

- **Runs in your browser tab**: DraftBlaster interacts directly with the Gmail webpage (`mail.google.com`) on your computer.
- **No external servers or databases**: No data ever leaves your computer except when Gmail sends your email through Google's official servers.
- **Why do we run `npm run build` once?**  
  The extension is written in TypeScript and React for safety and a modern UI. Web browsers only understand plain JavaScript. Running `npm run build` is simply a **one-time translator** that converts the code into static files in the `dist/` folder. Once built, Node/npm is finished and you never need to keep a terminal open.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        YOUR COMPUTER / BROWSER                          │
│                                                                         │
│  ┌───────────────────────┐             ┌─────────────────────────────┐  │
│  │   DraftBlaster Popup  │ ──────────> │ Gmail Web Tab               │  │
│  │   (Inside Chrome)     │ DOM clicks  │ (mail.google.com/#drafts)   │  │
│  └───────────┬───────────┘             └──────────────┬──────────────┘  │
│              │                                        │                 │
│              │ (Only if UI gets stuck)                │ Native Delivery │
│              ▼                                        ▼                 │
│  ┌───────────────────────┐             ┌─────────────────────────────┐  │
│  │ Google Gemini API     │             │ Google Mail Servers         │  │
│  │ (Client HTTPS call)   │             │ (Delivers your emails)      │  │
│  └───────────────────────┘             └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚦 Beginner Quick Start Guide

Follow these 3 simple steps to install and start using DraftBlaster:

### Step 1: Get Your Free Gemini API Key

DraftBlaster uses Google's Gemini AI purely as an intelligent fallback to recover navigation if Gmail pops up an unexpected modal or dialog.

1. Go to [Google AI Studio (aistudio.google.com)](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** and then **"Create API key"**.
4. Copy your API key (it starts with `AIza...`). Keep it handy—you will paste it directly into the extension UI!

---

### Step 2: Prepare the Extension Files (One-Time Build)

Make sure you have [Node.js](https://nodejs.org/) installed on your computer.

1. Open your computer's **Terminal** (or Command Prompt / PowerShell on Windows).
2. Navigate to the project directory:
   ```bash
   cd /path/to/draftblaster
   ```
3. Install the compilation tools:
   ```bash
   npm install
   ```
4. Compile the extension files:
   ```bash
   npm run build
   ```
   *You will now see a new folder called `dist/` created in the project folder. This contains the ready-to-use extension!*

---

### Step 3: Load the Extension into Google Chrome

1. Open **Google Chrome**.
2. Type `chrome://extensions` into your Chrome address bar and press **Enter**.
3. In the top-right corner, switch the **Developer mode** toggle to **ON** (blue).
4. In the top-left corner, click the **"Load unpacked"** button.
5. In the file picker, select the **`dist`** folder inside your `draftblaster` project folder and click **Select / Open**.
6. That's it! **DraftBlaster** is now installed in your browser.
7. Click the **Puzzle icon (Extensions)** in Chrome's top-right toolbar and click the **Pin 📌** icon next to DraftBlaster so it is always visible.

---

### Step 4: Load into Other Browsers

- **Opera**: Go to `opera://extensions` → enable **Developer Mode** (top-right) → click **Load unpacked** → select `dist/`.
- **Brave**: Go to `brave://extensions` → enable **Developer mode** → click **Load unpacked** → select `dist/`.
- **Microsoft Edge**: Go to `edge://extensions` → enable **Developer mode** (left sidebar) → click **Load unpacked** → select `dist/`.
- **Mozilla Firefox**: Go to `about:debugging#/runtime/this-firefox` → click **Load Temporary Add-on...** → select `manifest.json` inside the `dist/` folder.

---

## 🎯 Step-by-Step Usage Guide

### 1. Compose Your Drafts in Gmail
Open [Gmail](https://mail.google.com) and create the email drafts you want to send. Add the recipient email, subject line, email text, and any attachments. Leave them saved in your **Drafts** folder.

### 2. Navigate to Drafts View
Click on **Drafts** in Gmail's left sidebar, or go directly to:  
👉 **[https://mail.google.com/#drafts](https://mail.google.com/#drafts)**

### 3. Open DraftBlaster & Add Your API Key (First Time Only)
1. Click the **DraftBlaster 🚀** icon in your browser toolbar.
2. Click the **Gear icon (⚙️)** in the top right corner to open Settings.
3. Paste your **Gemini API Key** into the API Key field.
4. Click **Save Settings** (The key is securely saved into your browser's private storage and will be remembered even when you close Chrome).
5. Click the **X** to close Settings.

### 4. Scan and Send!
1. In the DraftBlaster popup, click the blue **"Scan Drafts"** button.
2. DraftBlaster will scan the drafts visible on your screen and display them in a list.
3. All drafts are automatically checked. If you want to skip any draft, uncheck its box.
4. Click **"SEND SELECTED"**.
5. A confirmation dialog will pop up showing the number of emails to be sent. Click **"CONFIRM & SEND"**.
6. DraftBlaster will open each draft, verify everything, and send it with human-like pacing.
7. **Need to pause?** Click the red **"STOP"** button at any time.

---

## 🧪 Practicing Safely with "Mock Mode"

If you want to test how DraftBlaster works without actually sending real emails to anyone:

1. Click the **DraftBlaster** icon → Click **Settings (⚙️)**.
2. Check the box for **"MOCK MODE (Test UI & flows without Gmail)"**.
3. Click **Save Settings**.
4. Now click **Scan Drafts** and **SEND SELECTED**.
5. DraftBlaster will simulate the entire scanning, validation, countdowns, and sending animations using mock data, with zero risk of sending an email.
6. Once you're comfortable, open Settings and turn Mock Mode **OFF**.

---

## ⚙️ Settings & Customization

| Setting | Default | What it does |
|---|---|---|
| **Gemini API Key** | Empty | Your Google Gemini API key used for UI navigation recovery. Stored exclusively on your computer in `chrome.storage.local`. |
| **Gemini Model** | `gemini-2.5-flash` | The AI model used for navigation analysis. |
| **Run Limit** | `500` | Maximum number of drafts to process in a single run. |
| **Min Delay (ms)** | `1500` | The minimum wait time (in milliseconds, 1.5s) between sending emails. |
| **Max Delay (ms)** | `4000` | The maximum wait time (in milliseconds, 4.0s) between sending emails. |
| **Mock Mode** | `Off` | Simulates the entire process with fake drafts for safe demonstration and testing. |

---

## ❓ Frequently Asked Questions (FAQ) & Troubleshooting

#### Q: Do I need to keep a terminal or command prompt open?
**No.** The terminal was only used for the one-time `npm run build` step. After loading the `dist/` folder into Chrome, you can close your terminal completely.

#### Q: When I close Chrome and reopen it tomorrow, do I have to set it up again?
**No.** Chrome remembers your loaded unpacked extension and all your saved settings (including your API key). It will be ready whenever you open Gmail.

#### Q: Will DraftBlaster modify the text or subject of my drafts?
**Never.** DraftBlaster has a strict read-and-send policy. It never edits your subject, body text, or attachments.

#### Q: The popup says "No drafts detected. Ensure Gmail Drafts is open."
Make sure you are on active tab `https://mail.google.com/#drafts` and have at least one draft in your Gmail account. Refresh the Gmail page and try clicking **Scan Drafts** again.

#### Q: Where is my API key stored? Is it sent to anyone?
Your API key is saved exclusively in your own browser's local sandbox storage (`chrome.storage.local`). It is never sent to any developer server or third party—only directly to Google's official Gemini endpoint when navigation recovery is needed.
