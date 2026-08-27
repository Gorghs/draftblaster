export type AutomationState =
  | 'IDLE'
  | 'GMAIL_NOT_READY'
  | 'DRAFTS_PAGE'
  | 'SCANNING'
  | 'DRAFT_LIST_READY'
  | 'OPENING_DRAFT'
  | 'DRAFT_OPEN'
  | 'VALIDATING'
  | 'READY_TO_SEND'
  | 'SENDING'
  | 'SEND_CONFIRMED'
  | 'RETURNING_TO_DRAFTS'
  | 'NEXT_DRAFT'
  | 'COMPLETED'
  | 'ERROR'
  | 'AI_RECOVERY'
  | 'STOPPED';

export type DraftStatus =
  | 'PENDING'
  | 'OPENING'
  | 'READY'
  | 'SENDING'
  | 'SENT'
  | 'FAILED'
  | 'UNKNOWN'
  | 'STOPPED'
  | 'SKIPPED';

export interface DraftItem {
  id: string;
  recipient: string;
  subject: string;
  preview: string;
  hasAttachment: boolean;
  isValidRecipient: boolean;
  status: DraftStatus;
  errorMessage?: string;
  rowIndex?: number;
}

export type AllowedAIAction =
  | 'OPEN_DRAFTS'
  | 'OPEN_SELECTED_DRAFT'
  | 'RETURN_TO_DRAFTS'
  | 'GO_BACK'
  | 'REFRESH'
  | 'WAIT'
  | 'CLOSE_DIALOG'
  | 'RETRY'
  | 'STOP';

export interface AIRecommendation {
  action: AllowedAIAction;
  confidence: number;
  reason: string;
}

export interface ExtensionSettings {
  runLimit: number;
  minDelayMs: number;
  maxDelayMs: number;
  geminiEnabled: boolean;
  geminiApiKey: string;
  geminiModel: string;
  geminiMinConfidence: number;
  maxAiRecoveryAttempts: number;
  requireConfirmation: boolean;
  mockMode: boolean;
}

export interface RunState {
  state: AutomationState;
  drafts: DraftItem[];
  selectedDraftIds: string[];
  currentIndex: number;
  totalToSend: number;
  sentCount: number;
  failedCount: number;
  skippedCount: number;
  currentDraftSubject?: string;
  currentDraftRecipient?: string;
  statusMessage: string;
  errorMessage?: string;
  isStopRequested: boolean;
  aiAttemptsCount: number;
}

// Chrome Message Actions
export type ExtensionMessage =
  | { type: 'GET_STATE' }
  | { type: 'SET_SETTINGS'; settings: Partial<ExtensionSettings> }
  | { type: 'SCAN_DRAFTS' }
  | { type: 'START_SEND'; draftIds: string[] }
  | { type: 'STOP_SEND' }
  | { type: 'RESET_RUN' }
  | { type: 'STATE_UPDATED'; state: RunState }
  | { type: 'GMAIL_STATUS_PING' };
