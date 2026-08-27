import { initRunController, handleExtensionMessage } from '../automation/runController';
import { detectCurrentGmailState } from './gmailStateDetector';

console.log('[DraftBlaster] Content script initialized on Gmail');

// Initialize controller in content script context
initRunController().then(() => {
  console.log('[DraftBlaster] Automation state machine ready in content context');
});

// Listen for messages from popup or background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GMAIL_STATUS_PING') {
    const status = detectCurrentGmailState();
    sendResponse({ isConnected: true, status });
    return false;
  }

  handleExtensionMessage(message, sendResponse);
  return true; // Asynchronous response support
});
