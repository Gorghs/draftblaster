import { describe, it, expect } from 'vitest';
import { validateAIRecommendation } from '../src/ai/aiActionValidator';

describe('AI Action Validator & Safety Boundary Tests', () => {
  it('should accept valid whitelisted navigation actions with sufficient confidence', () => {
    const response = {
      action: 'OPEN_DRAFTS',
      confidence: 0.95,
      reason: 'Current view is inbox, need to navigate to drafts',
    };
    const result = validateAIRecommendation(response, 0.70);
    expect(result.isValid).toBe(true);
    expect(result.action).toBe('OPEN_DRAFTS');
  });

  it('should REJECT any SEND / CLICK_SEND action as a critical security boundary', () => {
    const forbiddenList = [
      { action: 'SEND', confidence: 0.99, reason: 'Ready to send' },
      { action: 'CLICK_SEND', confidence: 0.99, reason: 'Click send button' },
      { action: 'SEND_EMAIL', confidence: 0.95, reason: 'Send the email' },
      { action: 'SUBMIT', confidence: 0.95, reason: 'Submit form' },
      { action: 'sendCurrentVerifiedDraft', confidence: 1.0, reason: 'Trigger function' },
    ];

    for (const testCase of forbiddenList) {
      const result = validateAIRecommendation(testCase, 0.70);
      expect(result.isValid).toBe(false);
      expect(result.rejectionReason).toContain('Security Violation');
    }
  });

  it('should reject unknown arbitrary actions', () => {
    const response = {
      action: 'DELETE_ALL_EMAILS',
      confidence: 0.95,
      reason: 'Testing unknown action',
    };
    const result = validateAIRecommendation(response, 0.70);
    expect(result.isValid).toBe(false);
    expect(result.rejectionReason).toContain('Unknown or disallowed action');
  });

  it('should reject actions with confidence below threshold', () => {
    const response = {
      action: 'OPEN_DRAFTS',
      confidence: 0.55,
      reason: 'Unsure about current view',
    };
    const result = validateAIRecommendation(response, 0.70);
    expect(result.isValid).toBe(false);
    expect(result.rejectionReason).toContain('below minimum threshold');
  });

  it('should reject malformed JSON or non-object payloads', () => {
    expect(validateAIRecommendation(null).isValid).toBe(false);
    expect(validateAIRecommendation('string').isValid).toBe(false);
    expect(validateAIRecommendation({}).isValid).toBe(false);
  });
});
