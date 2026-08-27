import { AllowedAIAction, AIRecommendation } from '../types';
import { ALLOWED_AI_ACTIONS, FORBIDDEN_AI_ACTIONS } from './aiSchemas';

export interface ValidationResult {
  isValid: boolean;
  action?: AllowedAIAction;
  confidence?: number;
  reason?: string;
  rejectionReason?: string;
}

/**
 * Strictly validates recommendations coming from Gemini.
 * Any non-whitelisted, forbidden, or low-confidence response is rejected.
 */
export function validateAIRecommendation(
  rawResponse: any,
  minConfidence: number = 0.70
): ValidationResult {
  if (!rawResponse || typeof rawResponse !== 'object') {
    return {
      isValid: false,
      rejectionReason: 'Malformed AI response: expected JSON object',
    };
  }

  const { action, confidence, reason } = rawResponse;

  if (typeof action !== 'string') {
    return {
      isValid: false,
      rejectionReason: 'Invalid AI response: missing or non-string "action"',
    };
  }

  const normalizedAction = action.trim().toUpperCase() as AllowedAIAction;

  // Check forbidden actions explicitly
  if (FORBIDDEN_AI_ACTIONS.includes(normalizedAction) || normalizedAction.includes('SEND')) {
    return {
      isValid: false,
      rejectionReason: `Security Violation: AI returned forbidden action "${action}". Send operations can only be deterministic.`,
    };
  }

  // Check whitelist
  if (!ALLOWED_AI_ACTIONS.includes(normalizedAction)) {
    return {
      isValid: false,
      rejectionReason: `Unknown or disallowed action: "${action}". Must be one of: ${ALLOWED_AI_ACTIONS.join(', ')}`,
    };
  }

  const confNum = Number(confidence);
  if (isNaN(confNum) || confNum < 0 || confNum > 1) {
    return {
      isValid: false,
      rejectionReason: `Invalid confidence score: ${confidence}`,
    };
  }

  if (confNum < minConfidence) {
    return {
      isValid: false,
      rejectionReason: `Confidence score ${confNum.toFixed(2)} is below minimum threshold ${minConfidence.toFixed(2)}`,
    };
  }

  return {
    isValid: true,
    action: normalizedAction,
    confidence: confNum,
    reason: typeof reason === 'string' ? reason.slice(0, 300) : 'No reason provided',
  };
}
