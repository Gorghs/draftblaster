import React, { useState, useEffect } from 'react';
import { ExtensionSettings, RunState, DraftItem } from '../types';
import { getSettings, saveSettings, DEFAULT_SETTINGS } from '../storage/settings';
import { getStoredRunState, INITIAL_RUN_STATE, resetStoredRunState, saveRunState } from '../storage/runState';
import { handleExtensionMessage } from '../automation/runController';
import { DraftList } from './components/DraftList';
import { SettingsModal } from './components/SettingsModal';
import { ConfirmationModal } from './components/ConfirmationModal';
import {
  Mail,
  Play,
  Square,
  RefreshCw,
  Settings as SettingsIcon,
  RotateCcw,
} from 'lucide-react';

export const App: React.FC = () => {
  const [settings, setSettings] = useState<ExtensionSettings>(DEFAULT_SETTINGS);
  const [runState, setRunState] = useState<RunState>(INITIAL_RUN_STATE);
  const [isGmailConnected, setIsGmailConnected] = useState<boolean>(false);
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [showConfirmation, setShowConfirmation] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const loadData = async () => {
    try {
      const [s, r] = await Promise.all([getSettings(), getStoredRunState()]);
      setSettings(s || DEFAULT_SETTINGS);
      setRunState(r || INITIAL_RUN_STATE);
    } catch (err) {
      console.warn('[DraftBlaster] Error loading data:', err);
    }
    checkGmailConnection();
  };

  const checkGmailConnection = () => {
    if (typeof chrome === 'undefined' || !chrome.tabs?.query) return;

    try {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (chrome.runtime?.lastError) {
          setIsGmailConnected(false);
          return;
        }
        const activeTab = tabs?.[0];
        if (activeTab?.id && activeTab?.url && activeTab.url.includes('mail.google.com')) {
          chrome.tabs.sendMessage(activeTab.id, { type: 'GMAIL_STATUS_PING' }, (response) => {
            if (chrome.runtime?.lastError || !response) {
              setIsGmailConnected(false);
            } else {
              setIsGmailConnected(true);
            }
          });
        } else {
          setIsGmailConnected(false);
        }
      });
    } catch {
      setIsGmailConnected(false);
    }
  };

  useEffect(() => {
    loadData();

    const listener = (message: any) => {
      if (message?.type === 'STATE_UPDATED' && message.state) {
        setRunState(message.state);
      }
    };

    if (typeof chrome !== 'undefined' && chrome.runtime?.onMessage) {
      chrome.runtime.onMessage.addListener(listener);
    }

    const interval = setInterval(checkGmailConnection, 3000);

    return () => {
      clearInterval(interval);
      if (typeof chrome !== 'undefined' && chrome.runtime?.onMessage) {
        chrome.runtime.onMessage.removeListener(listener);
      }
    };
  }, []);

  const sendTabMessage = (msg: any): Promise<any> => {
    return new Promise((resolve) => {
      if (settings.mockMode) {
        handleExtensionMessage(msg, (res) => resolve(res));
        return;
      }

      if (typeof chrome === 'undefined' || !chrome.tabs?.query) {
        resolve({ success: false, error: 'Extension tab API unavailable' });
        return;
      }

      try {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (chrome.runtime?.lastError) {
            resolve({ success: false, error: chrome.runtime.lastError.message });
            return;
          }
          const activeTab = tabs?.[0];
          if (!activeTab?.id) {
            resolve({ success: false, error: 'No active Gmail tab found. Open mail.google.com' });
            return;
          }
          chrome.tabs.sendMessage(activeTab.id, msg, (response) => {
            if (chrome.runtime?.lastError) {
              resolve({ success: false, error: chrome.runtime.lastError.message });
            } else {
              resolve(response);
            }
          });
        });
      } catch (err: any) {
        resolve({ success: false, error: err?.message || 'Failed to send tab message' });
      }
    });
  };

  const handleScan = async () => {
    setIsLoading(true);
    const res = await sendTabMessage({ type: 'SCAN_DRAFTS' });
    const fresh = await getStoredRunState();
    setRunState(fresh);
    setIsLoading(false);
    if (res && res.error) {
      showToast(`Scan issue: ${res.error}`);
    } else if (fresh.drafts.length === 0) {
      showToast('No drafts detected. Ensure Gmail Drafts is open.');
    } else {
      showToast(`Found ${fresh.drafts.length} drafts (${fresh.selectedDraftIds.length} selected).`);
    }
  };

  const handleStartSending = async () => {
    setShowConfirmation(false);
    const res = await sendTabMessage({
      type: 'START_SEND',
      draftIds: runState.selectedDraftIds,
    });
    if (res && res.error) {
      showToast(`Error starting send: ${res.error}`);
    }
  };

  const handleStop = async () => {
    await sendTabMessage({ type: 'STOP_SEND' });
  };

  const handleReset = async () => {
    await resetStoredRunState();
    const fresh = await getStoredRunState();
    setRunState(fresh);
  };

  const handleToggleSelect = (id: string) => {
    const current = [...runState.selectedDraftIds];
    const exists = current.includes(id);
    let updated: string[];
    if (exists) {
      updated = current.filter((x) => x !== id);
    } else {
      if (current.length >= settings.runLimit) {
        showToast(`Run limit reached (${settings.runLimit}). Increase in Settings ⚙️`);
        return;
      }
      updated = [...current, id];
    }
    const nextState = { ...runState, selectedDraftIds: updated };
    setRunState(nextState);
    saveRunState(nextState);
  };

  const handleSelectAll = () => {
    if (runState.drafts.length === 0) {
      showToast('No drafts found. Click Scan Drafts first.');
      return;
    }

    const validIds = runState.drafts.slice(0, settings.runLimit).map((d) => d.id);
    if (runState.drafts.length > settings.runLimit) {
      showToast(`Selected first ${settings.runLimit} drafts due to Run Limit.`);
    }
    const nextState = { ...runState, selectedDraftIds: validIds };
    setRunState(nextState);
    saveRunState(nextState);
  };

  const handleClearSelection = () => {
    const nextState = { ...runState, selectedDraftIds: [] };
    setRunState(nextState);
    saveRunState(nextState);
  };

  const isRunning = [
    'OPENING_DRAFT',
    'DRAFT_OPEN',
    'VALIDATING',
    'READY_TO_SEND',
    'SENDING',
    'NEXT_DRAFT',
    'AI_RECOVERY',
  ].includes(runState.state);

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '14px', position: 'relative' }}>
      {/* Toast Notification */}
      {toastMessage && (
        <div style={{
          position: 'absolute',
          top: '12px',
          left: '16px',
          right: '16px',
          backgroundColor: '#0284c7',
          color: '#ffffff',
          padding: '8px 12px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: 500,
          zIndex: 200,
          boxShadow: '0 10px 15px -3px rgba(0,0,0,0.5)',
          textAlign: 'center',
        }}>
          {toastMessage}
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <img
            src="/icons/icon32.png"
            alt="DraftBlaster"
            width={32}
            height={32}
            style={{
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(14, 165, 233, 0.4)',
              display: 'block',
            }}
          />
          <div>
            <h1 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.02em' }}>
              DraftBlaster 🚀
            </h1>
            <span style={{ fontSize: '11px', color: '#94a3b8' }}>
              Personal Gmail Draft Automation
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <button
            onClick={() => setShowSettings(true)}
            style={{
              padding: '6px 8px',
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: '#cbd5e1',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
            }}
          >
            <SettingsIcon size={14} />
          </button>
        </div>
      </div>

      {/* Status Bar */}
      <div style={{
        padding: '10px 12px',
        backgroundColor: '#1e293b',
        borderRadius: '8px',
        border: '1px solid #334155',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '12px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: settings.mockMode ? '#f59e0b' : isGmailConnected ? '#22c55e' : '#ef4444',
          }} />
          <span style={{ color: '#94a3b8' }}>
            Gmail: <strong style={{ color: '#f8fafc' }}>
              {settings.mockMode ? 'Mock Mode' : isGmailConnected ? 'Connected' : 'Not Connected'}
            </strong>
          </span>
        </div>

        <div style={{ color: '#94a3b8' }}>
          Run limit: <strong style={{ color: '#38bdf8' }}>{settings.runLimit}</strong>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
        <div style={{
          backgroundColor: '#1e293b',
          borderRadius: '8px',
          padding: '8px 10px',
          border: '1px solid #334155',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '11px', color: '#94a3b8' }}>Drafts</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc' }}>
            {runState.drafts.length}
          </div>
        </div>

        <div style={{
          backgroundColor: '#1e293b',
          borderRadius: '8px',
          padding: '8px 10px',
          border: '1px solid #334155',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '11px', color: '#94a3b8' }}>Sent</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#22c55e' }}>
            {runState.sentCount} <span style={{ fontSize: '10px', color: '#64748b' }}>/ {runState.totalToSend || runState.selectedDraftIds.length}</span>
          </div>
        </div>

        <div style={{
          backgroundColor: '#1e293b',
          borderRadius: '8px',
          padding: '8px 10px',
          border: '1px solid #334155',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '11px', color: '#94a3b8' }}>Failed</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: runState.failedCount > 0 ? '#ef4444' : '#64748b' }}>
            {runState.failedCount}
          </div>
        </div>
      </div>

      {/* Scan Button */}
      <button
        onClick={handleScan}
        disabled={isLoading || isRunning || (!isGmailConnected && !settings.mockMode)}
        style={{
          padding: '9px',
          backgroundColor: '#334155',
          border: '1px solid #475569',
          borderRadius: '8px',
          color: '#f8fafc',
          fontSize: '13px',
          fontWeight: 600,
          cursor: isLoading || isRunning || (!isGmailConnected && !settings.mockMode) ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
        }}
      >
        <RefreshCw size={15} className={isLoading ? 'animate-spin' : ''} />
        {isLoading ? 'Scanning...' : 'Scan Drafts'}
      </button>

      {/* Status / Live Progress Box */}
      {(isRunning || runState.state !== 'IDLE') && (
        <div style={{
          padding: '10px 12px',
          backgroundColor: runState.state === 'ERROR' ? 'rgba(239, 68, 68, 0.15)' : runState.state === 'AI_RECOVERY' ? 'rgba(168, 85, 247, 0.15)' : '#0f172a',
          border: `1px solid ${runState.state === 'ERROR' ? '#ef4444' : runState.state === 'AI_RECOVERY' ? '#a855f7' : '#334155'}`,
          borderRadius: '8px',
          fontSize: '12px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span style={{ color: '#94a3b8', fontWeight: 500 }}>
              {isRunning ? `Sending ${runState.currentIndex} / ${runState.totalToSend}` : 'Status'}
            </span>
            <span style={{
              fontWeight: 600,
              color: runState.state === 'COMPLETED' ? '#22c55e' : runState.state === 'AI_RECOVERY' ? '#c084fc' : '#38bdf8'
            }}>
              {runState.state}
            </span>
          </div>

          {runState.currentDraftRecipient && isRunning && (
            <div style={{ color: '#cbd5e1', fontSize: '11px', marginBottom: '2px' }}>
              Current: <strong>{runState.currentDraftRecipient}</strong>
            </div>
          )}

          <div style={{ color: '#f8fafc', fontSize: '12px', lineHeight: 1.3 }}>
            {runState.statusMessage}
          </div>
        </div>
      )}

      {/* Drafts List Container */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#cbd5e1' }}>
            Drafts ({runState.selectedDraftIds.length} selected)
          </span>
          <div style={{ display: 'flex', gap: '6px' }}>
            <button
              onClick={handleSelectAll}
              disabled={isRunning || runState.drafts.length === 0}
              style={{
                background: 'none',
                border: 'none',
                color: '#38bdf8',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
                padding: '2px 4px',
              }}
            >
              Select All
            </button>
            <span style={{ color: '#475569' }}>|</span>
            <button
              onClick={handleClearSelection}
              disabled={isRunning || runState.drafts.length === 0}
              style={{
                background: 'none',
                border: 'none',
                color: '#94a3b8',
                fontSize: '11px',
                cursor: 'pointer',
                padding: '2px 4px',
              }}
            >
              Clear
            </button>
          </div>
        </div>

        <DraftList
          drafts={runState.drafts}
          selectedIds={runState.selectedDraftIds}
          onToggleSelect={handleToggleSelect}
          disabled={isRunning}
        />
      </div>

      {/* Action Footer */}
      <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
        {isRunning ? (
          <button
            onClick={handleStop}
            style={{
              flex: 1,
              padding: '11px',
              backgroundColor: '#dc2626',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              fontSize: '14px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
            }}
          >
            <Square size={16} /> STOP
          </button>
        ) : (
          <>
            <button
              onClick={() => setShowConfirmation(true)}
              disabled={runState.selectedDraftIds.length === 0 || (!isGmailConnected && !settings.mockMode)}
              style={{
                flex: 1,
                padding: '11px',
                backgroundColor: runState.selectedDraftIds.length === 0 || (!isGmailConnected && !settings.mockMode) ? '#334155' : '#0284c7',
                border: 'none',
                borderRadius: '8px',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: 700,
                cursor: runState.selectedDraftIds.length === 0 || (!isGmailConnected && !settings.mockMode) ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
              }}
            >
              <Play size={16} /> SEND SELECTED ({runState.selectedDraftIds.length})
            </button>
            <button
              onClick={handleReset}
              style={{
                padding: '11px 14px',
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#94a3b8',
                cursor: 'pointer',
              }}
              title="Reset Run"
            >
              <RotateCcw size={16} />
            </button>
          </>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirmation && (
        <ConfirmationModal
          count={runState.selectedDraftIds.length}
          onConfirm={handleStartSending}
          onCancel={() => setShowConfirmation(false)}
        />
      )}

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal
          settings={settings}
          onSave={async (updated) => {
            const saved = await saveSettings(updated);
            setSettings(saved);
          }}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  );
};
