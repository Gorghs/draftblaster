# 🚀 DraftBlaster

> **Automate sending your Gmail drafts in bulk directly from your browser.**  
> **100% Client-Side • Zero Backend Servers Needed • Safe & Human-Paced**

---

## ⚡ Quick Setup & Installation (Step-by-Step)

### Step 1: Clone the Repository & Build
Open your terminal and run these commands:

```bash
# 1. Clone the repository
git clone https://github.com/Gorghs/draftblaster.git

# 2. Enter the project folder
cd draftblaster

# 3. Install dependencies
npm install

# 4. Build the extension (creates the dist folder)
npm run build
```

*(Once the build finishes, you can close your terminal. No server needs to remain running.)*

---

### Step 2: Load into Google Chrome (or Opera / Brave / Edge)

1. Open **Google Chrome**.
2. In the address bar, type `chrome://extensions` and press **Enter**.
3. Turn **ON** the **Developer mode** toggle switch in the top-right corner.
4. Click the **"Load unpacked"** button in the top-left corner.
5. In the file picker window, select the **`dist`** folder inside your `draftblaster` directory.
6. Click the **Extensions puzzle icon** in Chrome's top toolbar and click the **Pin 📌** icon next to DraftBlaster.

*(For **Opera**, open `opera://extensions` • For **Brave**, open `brave://extensions` • For **Edge**, open `edge://extensions`)*

---

### Step 3: Get a Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** → **"Create API key"** and copy it.

---

### Step 4: Add Your Key & Start Sending

1. Open [Gmail Drafts](https://mail.google.com/#drafts).
2. Click the **DraftBlaster 🚀** icon in your browser toolbar.
3. Click the **Gear icon (⚙️)** in the top right to open **Settings**.
4. Paste your **Gemini API Key** and click **Save Settings**.
5. Click **"Scan Drafts"**.
6. Select or review the drafts you want to send.
7. Click **"SEND SELECTED"** → Click **"CONFIRM & SEND"**.
8. DraftBlaster will automatically open and send each draft with human-like delays. You can click **STOP** at any time to pause.

---

## 🧪 Safe Practice with "Mock Mode"

Want to test the extension without sending real emails?

1. Click the **DraftBlaster** icon → Open **Settings (⚙️)**.
2. Check the box for **"MOCK MODE"** and click **Save Settings**.
3. Click **Scan Drafts** and **SEND SELECTED**.
4. The extension will run with simulated test drafts.
5. When ready to send real emails, turn **MOCK MODE** off in Settings.

---

## 🛡️ Key Features & Guarantees

- **Drafts Never Change**: Your email subject, body text, recipients, and attachments are never modified. DraftBlaster strictly clicks the native send button.
- **100% Client-Side**: No backend servers, no cloud databases, and no tracking.
- **Persistent Settings**: Your API key and settings stay saved in Chrome storage across browser restarts.
