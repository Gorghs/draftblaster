# Contributing to DraftBlaster 🚀

Thank you for your interest in contributing to DraftBlaster! We welcome pull requests, bug fixes, and feature proposals.

---

## 🌿 Branching Strategy

| Branch | Platform |
|---|---|
| `main` | Mozilla Firefox Edition (`.xpi` / Firefox MV3) |
| `chrome-extension` | Google Chrome, Brave, Opera, and Edge Edition |
| `feature/gmail-api-scheduler` | Headless Python Gmail API v1 OAuth 2.0 Scheduler |

---

## 🛠️ Local Development Setup

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/Gorghs/draftblaster.git
   cd draftblaster
   npm install
   ```

2. Run automated test suites:
   ```bash
   npm test
   ```

3. Compile extension bundles:
   ```bash
   npm run build
   ```

4. Create Firefox `.xpi` package:
   ```bash
   npm run build:xpi
   ```

---

## 🔒 Security Requirements for Pull Requests

- **Strict Client-Side Guarantee**: No PR introducing backend proxies, telemetry tracking, or external servers will be accepted for extension branches.
- **Draft Integrity**: Code must strictly preserve user draft content without modification.
- **AI Safety**: Navigation AI must remain logically quarantined from the sending execution path.
