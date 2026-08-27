import { getSettings } from '../storage/settings';
import { getStoredRunState } from '../storage/runState';

console.log('[DraftBlaster] Background Service Worker ready');

chrome.runtime.onInstalled.addListener(async () => {
  console.log('[DraftBlaster] Extension installed/updated');
  // Ensure default storage values exist
  await getSettings();
  await getStoredRunState();
});
