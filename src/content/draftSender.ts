import {
  findComposeWindow,
  findRecipient,
  findSubject,
  findSendButton,
  findSendConfirmation,
  findCloseDraftButton,
} from './gmailSelectors';
import { waitForCondition } from './gmailStateDetector';
import { STANDARD_DELAYS, humanDelay } from '../automation/humanDelay';
import { DraftItem } from '../types';

export interface SendVerificationResult {
  canSend: boolean;
  reason?: string;
  foundRecipient?: string;
  foundSubject?: string;
}

/**
 * Send Safety Checks:
 * 1. A compose/draft window is open.
 * 2. The Send button exists and is enabled.
 * 3. The user explicitly confirmed the batch.
 */
export function verifyDraftBeforeSend(
  expectedDraft: DraftItem,
  isBatchUserConfirmed: boolean
): SendVerificationResult {
  if (!isBatchUserConfirmed) {
    return { canSend: false, reason: 'Batch was not confirmed by user.' };
  }

  const compose = findComposeWindow();
  if (!compose) {
    return { canSend: false, reason: 'No active compose or draft window is open.' };
  }

  const { email: foundRecipient } = findRecipient(compose);
  const { subject: foundSubject } = findSubject(compose);

  const sendBtn = findSendButton(compose);
  if (!sendBtn) {
    return { canSend: false, reason: 'Send button is not found in compose window.' };
  }

  if (sendBtn.getAttribute('aria-disabled') === 'true' || (sendBtn as HTMLButtonElement).disabled) {
    return { canSend: false, reason: 'Send button is currently disabled.' };
  }

  return {
    canSend: true,
    foundRecipient: foundRecipient || expectedDraft.recipient,
    foundSubject: foundSubject || expectedDraft.subject,
  };
}

/**
 * Deterministic Send execution.
 * CRITICAL ARCHITECTURE RULE: Gemini must NEVER call this function.
 */
export async function sendCurrentVerifiedDraft(): Promise<{ success: boolean; error?: string; status: 'SENT' | 'FAILED' | 'UNKNOWN' }> {
  const compose = findComposeWindow();
  if (!compose) {
    return { success: false, error: 'Compose window closed before sending.', status: 'FAILED' };
  }

  const sendBtn = findSendButton(compose);
  if (!sendBtn) {
    return { success: false, error: 'Send button not available.', status: 'FAILED' };
  }

  // Pre-send human delay
  await STANDARD_DELAYS.beforeSend();

  // Natural click sequence with focus
  try {
    sendBtn.focus();
  } catch {}

  const mouseEvents = ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'];
  for (const evtType of mouseEvents) {
    sendBtn.dispatchEvent(
      new MouseEvent(evtType, {
        bubbles: true,
        cancelable: true,
        view: window,
      })
    );
  }
  try {
    sendBtn.click();
  } catch {}

  // Post-send verification: wait for compose window to close or toast to appear
  let confirmed = await waitForCondition(() => {
    const toast = findSendConfirmation();
    const isComposeClosed = findComposeWindow() === null;
    return toast !== null || isComposeClosed;
  }, 3500);

  // If still open after 3.5s, trigger Ctrl+Enter keyboard shortcut on compose as a solid fallback
  if (!confirmed && findComposeWindow()) {
    const activeCompose = findComposeWindow();
    if (activeCompose) {
      const targetInput = activeCompose.querySelector('div[role="textbox"], input[name="subjectbox"], [contenteditable="true"]') || activeCompose;
      const ctrlEnterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        ctrlKey: true,
        metaKey: true,
        bubbles: true,
        cancelable: true,
      });
      targetInput.dispatchEvent(ctrlEnterEvent);
    }

    confirmed = await waitForCondition(() => {
      const toast = findSendConfirmation();
      const isComposeClosed = findComposeWindow() === null;
      return toast !== null || isComposeClosed;
    }, 4500);
  }

  if (confirmed) {
    await STANDARD_DELAYS.afterSend();
    return { success: true, status: 'SENT' };
  }

  if (findComposeWindow()) {
    return { success: false, error: 'Send was triggered but draft window remained open.', status: 'UNKNOWN' };
  }

  return { success: true, status: 'SENT' };
}

export async function closeCurrentDraft(): Promise<void> {
  const compose = findComposeWindow();
  if (compose) {
    const closeBtn = findCloseDraftButton(compose);
    if (closeBtn) {
      closeBtn.click();
      await humanDelay(500, 1000);
    }
  }
}
