import { AutomationStateMachine } from './stateMachine';
import { getSettings, saveSettings } from '../storage/settings';
import { getStoredRunState, saveRunState, resetStoredRunState } from '../storage/runState';
import { ExtensionMessage, RunState } from '../types';

let stateMachineInstance: AutomationStateMachine | null = null;

export async function initRunController(): Promise<AutomationStateMachine> {
  const [initialState, settings] = await Promise.all([
    getStoredRunState(),
    getSettings(),
  ]);

  stateMachineInstance = new AutomationStateMachine(
    initialState,
    settings,
    async (newState: RunState) => {
      await saveRunState(newState);
      // Broadcast state update to popup if open
      try {
        chrome.runtime.sendMessage({
          type: 'STATE_UPDATED',
          state: newState,
        }).catch(() => {});
      } catch {}
    }
  );

  return stateMachineInstance;
}

export function getRunController(): AutomationStateMachine | null {
  return stateMachineInstance;
}

export async function handleExtensionMessage(
  message: ExtensionMessage,
  sendResponse: (response?: any) => void
) {
  if (!stateMachineInstance) {
    await initRunController();
  }

  switch (message.type) {
    case 'GET_STATE': {
      const state = await getStoredRunState();
      const settings = await getSettings();
      sendResponse({ state, settings });
      break;
    }
    case 'SET_SETTINGS': {
      const updated = await saveSettings(message.settings);
      stateMachineInstance?.updateSettings(updated);
      sendResponse({ success: true, settings: updated });
      break;
    }
    case 'SCAN_DRAFTS': {
      stateMachineInstance?.scan().then((drafts) => {
        sendResponse({ success: true, drafts });
      }).catch((err) => {
        sendResponse({ success: false, error: err.message });
      });
      return true; // Keep message channel open for async response
    }
    case 'START_SEND': {
      const [currentStored, currentSettings] = await Promise.all([
        getStoredRunState(),
        getSettings(),
      ]);
      if (stateMachineInstance) {
        stateMachineInstance.updateSettings(currentSettings);
        stateMachineInstance.syncRunState(currentStored);
      }
      stateMachineInstance?.startSending(message.draftIds).then(() => {
        sendResponse({ success: true });
      }).catch((err) => {
        sendResponse({ success: false, error: err.message });
      });
      return true;
    }
    case 'STOP_SEND': {
      stateMachineInstance?.stop();
      sendResponse({ success: true });
      break;
    }
    case 'RESET_RUN': {
      const resetState = await resetStoredRunState();
      sendResponse({ success: true, state: resetState });
      break;
    }
  }
}
