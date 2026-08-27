import { DraftItem } from '../types';
import { findDraftRows } from './gmailSelectors';

const EMAIL_REGEX = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/;

export function scanDraftRows(): DraftItem[] {
  const rows = findDraftRows();
  const drafts: DraftItem[] = [];

  rows.forEach((row, index) => {
    const rowText = row.innerText || '';
    const lines = rowText.split('\n').map((l) => l.trim()).filter(Boolean);

    // Look for recipient in attributes or elements
    let recipient = '';
    const emailEl = row.querySelector('[email], span[name], .yW span, [data-hovercard-id]');
    if (emailEl) {
      recipient = emailEl.getAttribute('email') || emailEl.getAttribute('data-hovercard-id') || (emailEl as HTMLElement).innerText || '';
    }
    if (!recipient) {
      const match = rowText.match(EMAIL_REGEX);
      if (match) {
        recipient = match[1];
      } else if (lines.length > 0) {
        recipient = lines[0];
      }
    }

    // Look for subject
    let subject = '';
    const subjectEl = row.querySelector('span.bog, span.bqe, [role="link"], [data-thread-id]');
    if (subjectEl) {
      subject = (subjectEl as HTMLElement).innerText.trim();
    }
    if (!subject && lines.length > 1) {
      subject = lines[1];
    } else if (!subject) {
      subject = lines[0] || '(Draft)';
    }

    // Look for preview
    let preview = '';
    const snippetEl = row.querySelector('span.y2, .y2');
    if (snippetEl) {
      preview = (snippetEl as HTMLElement).innerText.trim().replace(/^-\s*/, '');
    } else if (lines.length > 2) {
      preview = lines.slice(2).join(' ').slice(0, 100);
    }

    const hasAttachment = Boolean(row.querySelector('img[alt*="Attachment" i], span[aria-label*="Attachment" i], div[aria-label*="Attachment" i]'));

    // In Gmail Drafts view, every rendered row represents a draft in the user's Drafts folder
    const isValidRecipient = true;

    const stableId = `draft-${index}-${subject.slice(0, 20).replace(/\s+/g, '_')}`;

    drafts.push({
      id: stableId,
      recipient: recipient.trim() || 'Draft Recipient',
      subject: subject.trim(),
      preview: preview.trim(),
      hasAttachment,
      isValidRecipient,
      status: 'PENDING',
      rowIndex: index,
    });
  });

  return drafts;
}
