import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const manifestPath = path.join(__dirname, '..', 'dist', 'manifest.json');
if (fs.existsSync(manifestPath)) {
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  
  // Ensure dual compatibility for both Chrome (service_worker) and Firefox (scripts)
  if (manifest.background) {
    manifest.background.scripts = [manifest.background.service_worker || 'service-worker-loader.js'];
  }

  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
  console.log('✓ Injected Firefox background.scripts into dist/manifest.json for universal browser compatibility');
}
