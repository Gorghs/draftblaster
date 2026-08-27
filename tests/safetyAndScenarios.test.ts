import { describe, it, expect } from 'vitest';
import { verifyDraftBeforeSend } from '../src/content/draftSender';
import { DraftItem } from '../src/types';

describe('Send Safety Checks & Edge Case Tests', () => {
  const baseDraft: DraftItem = {
    id: 'test-1',
    recipient: 'test@example.com',
    subject: 'Application Test',
    preview: 'Test preview',
    hasAttachment: false,
    isValidRecipient: true,
    status: 'PENDING',
  };

  it('fails if user has not confirmed batch', () => {
    const result = verifyDraftBeforeSend(baseDraft, false);
    expect(result.canSend).toBe(false);
    expect(result.reason).toContain('Batch was not confirmed');
  });

  it('fails when compose window is missing from DOM', () => {
    const result = verifyDraftBeforeSend(baseDraft, true);
    expect(result.canSend).toBe(false);
    expect(result.reason).toContain('No active compose or draft window');
  });
});
