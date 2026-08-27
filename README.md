# DraftBlaster 🚀 (Firefox & Chromium / Opera Edition)

A **100% Client-Side Personal-Use Browser Extension** for Firefox (and Opera / Chromium) to automate sending selected Gmail drafts with human-like pacing, rigorous send-safety verifications, and Gemini AI navigation recovery.

---

## 🔒 Strict Client-Side Architecture

- **Zero Backend Servers**: No Express, Fastify, Flask, Node.js, Python, or external servers.
- **Zero Cloud Databases / BaaS**: No Firebase, Supabase, PostgreSQL, MongoDB, or Cloud Functions.
- **Zero Gmail API / OAuth**: Operates strictly via content scripts directly on Gmail's rendered web interface (`mail.google.com`).
- **Direct Gemini Client**: The extension interacts directly with Google's Gemini API for navigation recovery over client-side HTTPS.
- **Client-Side API Key Storage**: The Gemini API key is stored locally in your browser (`browser.storage.local` / `chrome.storage.local`).

---

## 🦊 How to Install and Load in Firefox

### Step 1: Build the Extension
```bash
cd /home/karthick/draftblaster
npm install
npm run build
```
The compiled static extension files will be placed into `/home/karthick/draftblaster/dist`.

### Step 2: Load into Firefox
1. Open **Firefox** and type `about:debugging#/runtime/this-firefox` in the address bar (or go to `about:debugging` → **This Firefox**).
2. Click **Load Temporary Add-on...**.
3. Navigate to `/home/karthick/draftblaster/dist` and select either `manifest.json` or `index.html`.
4. **DraftBlaster** is now installed and loaded in Firefox!

*(Note: In Opera or Chromium browsers, you can also load `/home/karthick/draftblaster/dist` directly via `opera://extensions` or `chrome://extensions` with **Developer mode** enabled.)*

---

## 🚦 How to Use in Firefox

1. Open [Gmail Drafts](https://mail.google.com/#drafts) in Firefox.
2. Click the **DraftBlaster** extension icon in your toolbar.
3. Open **Settings** (gear icon ⚙️) to:
   - Enter your **Gemini API Key**.
   - Confirm your Gemini Model (default: `gemini-2.5-flash`).
   - Adjust the **Run Limit** (default: 500).
   - Or enable **MOCK MODE** to test all animations and flows risk-free.
4. Click **Scan Drafts**.
5. All drafts are scanned and selected.
6. Click **SEND SELECTED** → Review in the confirmation popup → Click **CONFIRM & SEND**.
7. Watch the extension open and send each draft with human-paced delays. You can click **STOP** at any time to pause immediately.

---

## 🧪 Testing

Run all unit and safety tests:
```bash
npm test
```
