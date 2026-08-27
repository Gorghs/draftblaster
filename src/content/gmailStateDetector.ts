import { AutomationState } from '../types';
import {
  findComposeWindow,
  findDraftRows,
  findSendButton,
  findSendConfirmation,
  findActiveDialog,
} from './gmailSelectors';

export interface GmailStateContext {
  state: AutomationState;
  isDraftsUrl: boolean;
  hasComposeWindow: boolean;
  hasSendButton: boolean;
  draftsCount: number;
  dialogPresent: boolean;
  dialogTitle?: string;
  hasSendConfirmation: boolean;
  url: string;
}

export function detectCurrentGmailState(): GmailStateContext {
  const url = window.location.href;
  const isDraftsUrl = url.includes('#drafts') || url.includes('/drafts');
  const composeWindow = findComposeWindow();
  const hasComposeWindow = composeWindow !== null && composeWindow.offsetParent !== null;
  const sendButton = hasComposeWindow ? findSendButton(composeWindow) : null;
  const hasSendButton = sendButton !== null;
  const draftsCount = findDraftRows().length;
  const dialog = findActiveDialog();
  const dialogPresent = dialog !== null && dialog.offsetParent !== null;
  const dialogTitle = dialog ? (dialog.getAttribute('aria-label') || dialog.innerText?.slice(0, 50)) : undefined;
  const hasSendConfirmation = findSendConfirmation() !== null;

  let state: AutomationState = 'IDLE';

  if (!url.includes('mail.google.com')) {
    state = 'GMAIL_NOT_READY';
  } else if (dialogPresent) {
    state = 'AI_RECOVERY';
  } else if (hasSendConfirmation) {
    state = 'SEND_CONFIRMED';
  } else if (hasComposeWindow && hasSendButton) {
    state = 'READY_TO_SEND';
  } else if (hasComposeWindow) {
    state = 'DRAFT_OPEN';
  } else if (isDraftsUrl) {
    state = draftsCount > 0 ? 'DRAFT_LIST_READY' : 'DRAFTS_PAGE';
  } else {
    state = 'GMAIL_NOT_READY';
  }

  return {
    state,
    isDraftsUrl,
    hasComposeWindow,
    hasSendButton,
    draftsCount,
    dialogPresent,
    dialogTitle,
    hasSendConfirmation,
    url,
  };
}

/**
 * Waits for a specific DOM condition using MutationObserver.
 */
export function waitForCondition(
  predicate: () => boolean,
  timeoutMs: number = 8000
): Promise<boolean> {
  if (predicate()) return Promise.resolve(true);

  return new Promise((resolve) => {
    let timeoutId: any;
    const observer = new MutationObserver(() => {
      if (predicate()) {
        clearTimeout(timeoutId);
        observer.disconnect();
        resolve(true);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
    });

    timeoutId = setTimeout(() => {
      observer.disconnect();
      resolve(predicate());
    }, timeoutMs);
  });
}
