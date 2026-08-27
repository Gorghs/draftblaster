/**
 * Gmail Semantic & Accessible DOM Selectors
 * Designed to rely on aria-labels, accessible roles, semantic relationships, and stable DOM patterns
 * rather than obfuscated/dynamic Gmail CSS classes.
 */

export const GMAIL_SELECTORS = {
  // Navigation
  draftsNavLinks: [
    'a[href*="#drafts"]',
    'a[aria-label*="Drafts" i]',
    'a[title*="Drafts" i]',
    '[role="navigation"] [data-tooltip*="Drafts" i]',
    'div[data-tooltip*="Drafts" i]',
    'div[role="treeitem"][aria-label*="Drafts" i]',
    'div[role="treeitem"][data-tooltip*="Drafts" i]',
  ],

  // Draft rows in the list
  draftRows: [
    'tr[role="row"]',
    'div[role="main"] tbody tr',
    'div[role="row"]',
    'div[role="main"] table tr',
    'table.F.cf.zt tbody tr',
  ],

  // Main email list container
  mainContent: [
    'div[role="main"]',
    '[role="main"] table',
    '.AO',
  ],

  // Compose / Open Draft Window
  composeWindow: [
    'div.AD',
    'div[role="dialog"][aria-label*="Draft" i]',
    'div[role="dialog"][aria-label*="Compose" i]',
    'div[role="dialog"][aria-label*="Message" i]',
    'div[role="region"][aria-label*="Draft" i]',
    'div[role="region"][aria-label*="Compose" i]',
    'div.aaZ',
    'div.dw .AD',
  ],

  // Recipient input / pills in open compose
  composeRecipient: [
    'input[name="to"]',
    'input[aria-label*="To" i]',
    'input[peoplekit-id]',
    'span[email]',
    'div[aria-label*="To recipients" i] span[email]',
    'div[data-hovercard-id]',
    'div[role="combobox"][aria-label*="To" i]',
    'textarea[name="to"]',
    'div[name="to"]',
  ],

  // Subject in open compose
  composeSubject: [
    'input[name="subjectbox"]',
    'input[aria-label*="Subject" i]',
    'input[placeholder*="Subject" i]',
    'input[name="subject"]',
  ],

  // Send Button (strictly targets Send, excludes Schedule Send arrow)
  sendButton: [
    'div[role="button"][data-tooltip*="Send" i]:not([data-tooltip*="Schedule" i])',
    'div[role="button"][aria-label*="Send" i]:not([aria-label*="More" i]):not([aria-label*="Schedule" i])',
    'div.aoO',
    'div.T-I-atl',
    'div[role="button"][data-tooltip*="⌘Enter" i]',
    'div[role="button"][data-tooltip*="Ctrl-Enter" i]',
    'button[aria-label*="Send" i]',
  ],

  // Back / Discard / Close buttons
  backButton: [
    'div[role="button"][aria-label*="Back" i]',
    'div[role="button"][data-tooltip*="Back" i]',
    'button[aria-label*="Back" i]',
    'div[role="button"][aria-label*="Back to Drafts" i]',
  ],

  closeDraftButton: [
    'img[aria-label*="Save & close" i]',
    'img[aria-label*="Save and close" i]',
    'img[aria-label*="Close" i]',
    'div[role="button"][aria-label*="Save & close" i]',
    'div[role="button"][aria-label*="Save and close" i]',
    'div[role="button"][aria-label*="Close" i]',
  ],

  // Dialogs & banners
  dialogs: [
    'div[role="alertdialog"]',
    'div[role="dialog"]:not([aria-label*="Message" i]):not([aria-label*="Draft" i]):not(.AD)',
    '.Kj-JD',
  ],

  // Toast / Confirmation message
  sendConfirmation: [
    'div[role="status"]',
    'div[role="alert"]',
    'span.bAq',
    '.vh',
  ],
};

function getSafeDocument(): Document | null {
  if (typeof document !== 'undefined') return document;
  return null;
}

export function findFirstElement<T extends HTMLElement = HTMLElement>(
  selectors: string[],
  root?: Document | HTMLElement
): T | null {
  const targetRoot = root || getSafeDocument();
  if (!targetRoot) return null;

  for (const selector of selectors) {
    try {
      const el = targetRoot.querySelector<T>(selector);
      if (el) return el;
    } catch {}
  }
  return null;
}

export function findAllElements<T extends HTMLElement = HTMLElement>(
  selectors: string[],
  root?: Document | HTMLElement
): T[] {
  const targetRoot = root || getSafeDocument();
  if (!targetRoot) return [];

  for (const selector of selectors) {
    try {
      const els = Array.from(targetRoot.querySelectorAll<T>(selector));
      if (els.length > 0) return els;
    } catch {}
  }
  return [];
}

export function findDraftsNavigation(): HTMLElement | null {
  return findFirstElement(GMAIL_SELECTORS.draftsNavLinks);
}

export function findDraftRows(): HTMLElement[] {
  const doc = getSafeDocument();
  if (!doc) return [];
  const main = findFirstElement(GMAIL_SELECTORS.mainContent, doc) || doc;
  const rows = findAllElements(GMAIL_SELECTORS.draftRows, main);
  return rows.filter((row) => {
    const text = row.innerText || '';
    return text.trim().length > 0 && !row.querySelector('th');
  });
}

export function findDraftRow(identifier: { subject?: string; recipient?: string; rowIndex?: number }): HTMLElement | null {
  const rows = findDraftRows();
  if (rows.length === 0) return null;

  const targetSubj = (identifier.subject || '').toLowerCase().trim();
  const isGenericSubj = !targetSubj || targetSubj === '(no subject)' || targetSubj === '(draft)' || targetSubj === 'draft';
  const targetRecip = (identifier.recipient || '').toLowerCase().trim();
  const isGenericRecip = !targetRecip || targetRecip === 'draft' || targetRecip === 'draft recipient';

  // 1. Best match: both subject and recipient found in row
  if (!isGenericSubj && !isGenericRecip) {
    for (const row of rows) {
      const rowText = (row.innerText || '').toLowerCase();
      if (rowText.includes(targetSubj) && rowText.includes(targetRecip)) {
        return row;
      }
    }
  }

  // 2. Try matching by non-generic subject
  if (!isGenericSubj) {
    for (const row of rows) {
      const rowText = (row.innerText || '').toLowerCase();
      if (rowText.includes(targetSubj)) {
        return row;
      }
    }
  }

  // 3. Try matching by non-generic recipient
  if (!isGenericRecip) {
    for (const row of rows) {
      const rowText = (row.innerText || '').toLowerCase();
      if (rowText.includes(targetRecip)) {
        return row;
      }
    }
  }

  // 4. Default to top draft row in Drafts list (since previously sent drafts are removed)
  return rows[0] || null;
}

export function findComposeWindow(): HTMLElement | null {
  const doc = getSafeDocument();
  if (!doc) return null;

  // Search through all matching compose containers
  const candidates = findAllElements(GMAIL_SELECTORS.composeWindow, doc);
  for (const candidate of candidates) {
    // Verify candidate is an actual compose container (contains send button or subject input or message body)
    const hasSendBtn = candidate.querySelector('[data-tooltip*="Send" i], [aria-label*="Send" i], .aoO, .T-I-atl');
    const hasSubject = candidate.querySelector('input[name="subjectbox"], input[aria-label*="Subject" i]');
    const hasTo = candidate.querySelector('input[name="to"], input[aria-label*="To" i], [role="combobox"]');
    const hasBody = candidate.querySelector('div[aria-label*="Message Body" i], div[role="textbox"]');

    if (hasSendBtn || hasSubject || hasTo || hasBody || candidate.classList.contains('AD')) {
      return candidate;
    }
  }

  // Fallback to first matching selector
  return findFirstElement(GMAIL_SELECTORS.composeWindow, doc);
}

export function findSendButton(composeRoot?: HTMLElement): HTMLElement | null {
  const doc = getSafeDocument();
  const root = composeRoot || findComposeWindow() || (doc ? doc.body : undefined);
  if (!root) return null;

  const btn = findFirstElement(GMAIL_SELECTORS.sendButton, root);
  if (btn) return btn;

  // Fallback: search any button or role="button" with "Send" in text or attributes (excluding Schedule send)
  const buttons = Array.from(root.querySelectorAll<HTMLElement>('div[role="button"], button'));
  for (const b of buttons) {
    const label = (b.getAttribute('aria-label') || b.getAttribute('data-tooltip') || b.innerText || '').toLowerCase().trim();
    if ((label === 'send' || label.startsWith('send ') || label.includes('send \u2318enter') || label.includes('send ctrl-enter')) && !label.includes('schedule') && !label.includes('more')) {
      return b;
    }
  }

  return null;
}

export function findRecipient(composeRoot?: HTMLElement): { email: string; element: HTMLElement | null } {
  const doc = getSafeDocument();
  const root = composeRoot || findComposeWindow() || (doc ? doc.body : undefined);
  if (!root) return { email: '', element: null };

  const el = findFirstElement(GMAIL_SELECTORS.composeRecipient, root);
  let email = '';
  if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
    email = el.value.trim();
  }
  if (!email && el) {
    email = el.getAttribute('email') || el.getAttribute('data-hovercard-id') || el.innerText.trim();
  }

  if (!email) {
    const chip = root.querySelector('[email], [data-hovercard-id]');
    if (chip) {
      email = chip.getAttribute('email') || chip.getAttribute('data-hovercard-id') || (chip as HTMLElement).innerText.trim();
    }
  }

  return { email, element: el };
}

export function findSubject(composeRoot?: HTMLElement): { subject: string; element: HTMLElement | null } {
  const doc = getSafeDocument();
  const root = composeRoot || findComposeWindow() || (doc ? doc.body : undefined);
  if (!root) return { subject: '', element: null };

  const el = findFirstElement(GMAIL_SELECTORS.composeSubject, root);
  let subject = '';
  if (el instanceof HTMLInputElement) {
    subject = el.value.trim();
  } else if (el) {
    subject = el.innerText.trim();
  }
  return { subject, element: el };
}

export function findBackButton(): HTMLElement | null {
  return findFirstElement(GMAIL_SELECTORS.backButton);
}

export function findCloseDraftButton(composeRoot?: HTMLElement): HTMLElement | null {
  const doc = getSafeDocument();
  const root = composeRoot || findComposeWindow() || (doc ? doc.body : undefined);
  if (!root) return null;
  return findFirstElement(GMAIL_SELECTORS.closeDraftButton, root);
}

export function findActiveDialog(): HTMLElement | null {
  return findFirstElement(GMAIL_SELECTORS.dialogs);
}

export function findSendConfirmation(): HTMLElement | null {
  const toasts = findAllElements(GMAIL_SELECTORS.sendConfirmation);
  for (const toast of toasts) {
    const txt = (toast.innerText || '').toLowerCase();
    if (txt.includes('message sent') || txt.includes('sending') || txt.includes('undo')) {
      return toast;
    }
  }
  return null;
}
