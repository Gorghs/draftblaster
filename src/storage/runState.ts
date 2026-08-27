import { RunState } from '../types';

export const INITIAL_RUN_STATE: RunState = {
  state: 'IDLE',
  drafts: [],
  selectedDraftIds: [],
  currentIndex: 0,
  totalToSend: 0,
  sentCount: 0,
  failedCount: 0,
  skippedCount: 0,
  statusMessage: 'Ready. Open Gmail Drafts and click Scan.',
  isStopRequested: false,
  aiAttemptsCount: 0,
};

const RUN_STATE_KEY = 'draftblaster_run_state';

export async function getStoredRunState(): Promise<RunState> {
  try {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      const data = await chrome.storage.local.get(RUN_STATE_KEY);
      if (data && data[RUN_STATE_KEY]) {
        return { ...INITIAL_RUN_STATE, ...data[RUN_STATE_KEY] };
      }
    }
  } catch (err) {
    console.warn('[DraftBlaster] Failed to load run state:', err);
  }
  return { ...INITIAL_RUN_STATE };
}

export async function saveRunState(state: Partial<RunState>): Promise<RunState> {
  const current = await getStoredRunState();
  const updated = { ...current, ...state };
  try {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      await chrome.storage.local.set({ [RUN_STATE_KEY]: updated });
    }
  } catch (err) {
    console.error('[DraftBlaster] Failed to save run state:', err);
  }
  return updated;
}

export async function resetStoredRunState(): Promise<RunState> {
  return await saveRunState(INITIAL_RUN_STATE);
}
