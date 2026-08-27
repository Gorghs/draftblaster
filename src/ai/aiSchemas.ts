import { AllowedAIAction } from '../types';

export const ALLOWED_AI_ACTIONS: AllowedAIAction[] = [
  'OPEN_DRAFTS',
  'OPEN_SELECTED_DRAFT',
  'RETURN_TO_DRAFTS',
  'GO_BACK',
  'REFRESH',
  'WAIT',
  'CLOSE_DIALOG',
  'RETRY',
  'STOP',
];

// STRICT SECURITY BOUNDARY: Actions that AI must NEVER be allowed to execute
export const FORBIDDEN_AI_ACTIONS = [
  'SEND',
  'CLICK_SEND',
  'SEND_EMAIL',
  'SUBMIT',
  'sendCurrentVerifiedDraft',
];

export interface NavigationContext {
  url: string;
  automationState: string;
  expectedState: string;
  visibleTextSummary: string;
  dialogPresent: boolean;
  dialogTitle?: string;
  errorMessage?: string;
}
