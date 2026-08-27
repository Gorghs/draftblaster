# DraftBlaster 🚀

A **100% Client-Side Personal-Use Browser Extension** (Manifest V3) for **Chrome, Opera, Brave, Edge, and Firefox** to automate sending selected Gmail drafts with human-like pacing, rigorous send-safety verifications, and Gemini AI navigation recovery.

---

## 🔒 Strict Client-Side Architecture

- **Zero Backend Servers**: No Express, Fastify, Flask, Node.js, Python, or external servers.
- **Zero Cloud Databases / BaaS**: No Firebase, Supabase, PostgreSQL, MongoDB, or Cloud Functions.
- **Zero Gmail API / OAuth**: Operates strictly via content scripts directly on Gmail's rendered web interface (`mail.google.com`).
- **Direct Gemini Client**: The extension interacts directly with Google's Gemini API for navigation recovery over client-side HTTPS.
- **Client-Side API Key Storage**: The Gemini API key is stored locally in your browser (`chrome.storage.local`).

---

## 🛠️ Setup & Development

### 1. Configure Environment Variables
Create a local `.env` file (ignored by git so secrets are never pushed):
```bash
cp .env.example .env
```
Edit `.env` to include your Gemini API Key:
```env
VITE_GEMINI_API_KEY=your_gemini_api_key_here
VITE_GEMINI_MODEL=gemini-2.5-flash
```

### 2. Development Mode vs. Production Build

| Command | Purpose | When to Use |
|---|---|---|
| `npm run dev` | **Live Development Server** | Runs Vite with HMR (Hot Module Replacement via `@crxjs/vite-plugin`). Great when actively writing code or tweaking UI, as changes reload automatically in Chrome. |
| `npm run build` | **Production Static Build** | Bundles TypeScript & React into the static `dist/` directory. This generates the folder you load into Chrome or Firefox. |

---

## 🌐 How to Install & Load in Google Chrome / Opera / Brave / Edge

### Step 1: Build the Extension
```bash
npm install
npm run build
```
This compiles the extension into the `dist/` directory.

### Step 2: Load into Chrome / Chromium
1. Open Google Chrome and go to `chrome://extensions`.
2. Turn on the **Developer mode** toggle (top-right corner).
3. Click the **Load unpacked** button (top-left).
4. Select the `dist/` folder inside this project repository.
5. **DraftBlaster** is now installed and accessible from your browser toolbar!

*(For **Opera**, open `opera://extensions` and click **Load unpacked**. For **Brave**, visit `brave://extensions`.)*

---

## 🦊 How to Install & Load in Firefox

1. Build the extension (`npm run build`).
2. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`.
3. Click **Load Temporary Add-on...**.
4. Select the `manifest.json` file inside the `dist/` directory.

---

## 🚦 How to Use

1. Open [Gmail Drafts](https://mail.google.com/#drafts) in your browser.
2. Click the **DraftBlaster** extension icon in your toolbar.
3. Open **Settings** (gear icon ⚙️) to:
   - Verify or update your **Gemini API Key**.
   - Select your Gemini Model (default: `gemini-2.5-flash`).
   - Adjust the **Run Limit** (default: 500).
   - Or enable **MOCK MODE** to test all animations and flows risk-free.
4. Click **Scan Drafts**.
5. Select or review the drafts you want to send.
6. Click **SEND SELECTED** → Review in the confirmation modal → Click **CONFIRM & SEND**.
7. DraftBlaster will open and send each draft with human-paced delays. You can click **STOP** at any time to halt immediately.

---

## 🧪 Testing

Run the automated test suite:
```bash
npm test
```
