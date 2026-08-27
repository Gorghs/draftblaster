import { ExtensionSettings } from '../types';

export const DEFAULT_SETTINGS: ExtensionSettings = {
  runLimit: 500,
  minDelayMs: 1500,
  maxDelayMs: 4000,
  geminiEnabled: true,
  geminiApiKey: (import.meta as any).env?.VITE_GEMINI_API_KEY || '',
  geminiModel: (import.meta as any).env?.VITE_GEMINI_MODEL || 'gemini-2.5-flash',
  geminiMinConfidence: 0.70,
  maxAiRecoveryAttempts: 2,
  requireConfirmation: true,
  mockMode: false,
};

const SETTINGS_KEY = 'draftblaster_settings';

export async function getSettings(): Promise<ExtensionSettings> {
  try {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      const data = await chrome.storage.local.get(SETTINGS_KEY);
      if (data && data[SETTINGS_KEY]) {
        return { ...DEFAULT_SETTINGS, ...data[SETTINGS_KEY] };
      }
    }
  } catch (err) {
    console.warn('[DraftBlaster] Failed to load settings from storage, using defaults:', err);
  }
  return { ...DEFAULT_SETTINGS };
}

export async function saveSettings(settings: Partial<ExtensionSettings>): Promise<ExtensionSettings> {
  const current = await getSettings();
  const updated = { ...current, ...settings };
  try {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      await chrome.storage.local.set({ [SETTINGS_KEY]: updated });
    }
  } catch (err) {
    console.error('[DraftBlaster] Failed to save settings to storage:', err);
  }
  return updated;
}
