import React, { useState } from 'react';
import { ExtensionSettings } from '../../types';
import { Save, X, Key, ShieldCheck, Cpu, Sliders } from 'lucide-react';

interface Props {
  settings: ExtensionSettings;
  onSave: (settings: Partial<ExtensionSettings>) => void;
  onClose: () => void;
}

export const SettingsModal: React.FC<Props> = ({ settings, onSave, onClose }) => {
  const [formData, setFormData] = useState<ExtensionSettings>({ ...settings });
  const [showKey, setShowKey] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      onClose();
    }, 800);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '16px',
      zIndex: 100,
    }}>
      <div style={{
        backgroundColor: '#1e293b',
        borderRadius: '12px',
        border: '1px solid #334155',
        width: '100%',
        maxHeight: '92vh',
        overflowY: 'auto',
        padding: '20px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', color: '#f8fafc' }}>
            <Sliders size={20} color="#38bdf8" /> Extension Settings
          </h2>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* Gemini API Key */}
          <div>
            <label style={{ fontSize: '12px', fontWeight: 500, color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Key size={14} color="#f59e0b" /> Gemini API Key (Client-Side Storage)
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showKey ? 'text' : 'password'}
                value={formData.geminiApiKey}
                onChange={(e) => setFormData({ ...formData, geminiApiKey: e.target.value })}
                placeholder="Paste Gemini API Key..."
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  paddingRight: '60px',
                  backgroundColor: '#0f172a',
                  border: '1px solid #475569',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '13px',
                }}
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                style={{
                  position: 'absolute',
                  right: '8px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#94a3b8',
                  fontSize: '11px',
                  cursor: 'pointer',
                }}
              >
                {showKey ? 'Hide' : 'Show'}
              </button>
            </div>
            <p style={{ fontSize: '11px', color: '#94a3b8', margin: '4px 0 0 0' }}>
              Stored locally in your browser (chrome.storage.local) for personal testing.
            </p>
          </div>

          {/* Gemini Model */}
          <div>
            <label style={{ fontSize: '12px', fontWeight: 500, color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
              <Cpu size={14} color="#a855f7" /> Gemini Model
            </label>
            <input
              type="text"
              value={formData.geminiModel}
              onChange={(e) => setFormData({ ...formData, geminiModel: e.target.value })}
              placeholder="e.g. gemini-2.5-flash"
              style={{
                width: '100%',
                padding: '8px 12px',
                backgroundColor: '#0f172a',
                border: '1px solid #475569',
                borderRadius: '6px',
                color: '#f8fafc',
                fontSize: '13px',
              }}
            />
          </div>

          {/* Safety & Limits */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '12px', fontWeight: 500, color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>
                Run Limit
              </label>
              <input
                type="number"
                min="1"
                max="1000"
                value={formData.runLimit}
                onChange={(e) => setFormData({ ...formData, runLimit: parseInt(e.target.value) || 500 })}
                style={{
                  width: '100%',
                  padding: '8px',
                  backgroundColor: '#0f172a',
                  border: '1px solid #475569',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '13px',
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', fontWeight: 500, color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>
                AI Min Confidence
              </label>
              <input
                type="number"
                step="0.05"
                min="0.5"
                max="1.0"
                value={formData.geminiMinConfidence}
                onChange={(e) => setFormData({ ...formData, geminiMinConfidence: parseFloat(e.target.value) || 0.70 })}
                style={{
                  width: '100%',
                  padding: '8px',
                  backgroundColor: '#0f172a',
                  border: '1px solid #475569',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '13px',
                }}
              />
            </div>
          </div>

          {/* Checkboxes */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '4px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#e2e8f0', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.geminiEnabled}
                onChange={(e) => setFormData({ ...formData, geminiEnabled: e.target.checked })}
                style={{ accentColor: '#38bdf8' }}
              />
              <span>Enable Gemini AI navigation recovery</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#f59e0b', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.mockMode}
                onChange={(e) => setFormData({ ...formData, mockMode: e.target.checked })}
                style={{ accentColor: '#f59e0b' }}
              />
              <span><strong>MOCK MODE</strong> (Test UI & flows without Gmail)</span>
            </label>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '12px' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '8px 14px',
                backgroundColor: '#334155',
                border: 'none',
                borderRadius: '6px',
                color: '#f8fafc',
                fontSize: '13px',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              style={{
                padding: '8px 18px',
                backgroundColor: savedSuccess ? '#22c55e' : '#0284c7',
                border: 'none',
                borderRadius: '6px',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'background 0.2s',
              }}
            >
              {savedSuccess ? <ShieldCheck size={16} /> : <Save size={16} />}
              {savedSuccess ? 'Saved!' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
