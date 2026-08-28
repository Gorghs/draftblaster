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

function getStorage() {
  if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    return chrome.storage.local;
  }
  if (typeof (globalThis as any).browser !== 'undefined' && (globalThis as any).browser.storage?.local) {
    return (globalThis as any).browser.storage.local;
  }
  return null;
}

export async function getStoredRunState(): Promise<RunState> {
  try {
    const storage = getStorage();
    if (storage) {
      const data = await storage.get(RUN_STATE_KEY);
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
    const storage = getStorage();
    if (storage) {
      await storage.set({ [RUN_STATE_KEY]: updated });
    }
  } catch (err) {
    console.error('[DraftBlaster] Failed to save run state:', err);
  }
  return updated;
}

export async function resetStoredRunState(): Promise<RunState> {
  return await saveRunState(INITIAL_RUN_STATE);
}
