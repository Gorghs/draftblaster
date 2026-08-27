import React from 'react';
import { DraftItem } from '../../types';
import { Paperclip, CheckCircle, XCircle, Clock, AlertCircle, HelpCircle } from 'lucide-react';

interface Props {
  drafts: DraftItem[];
  selectedIds: string[];
  onToggleSelect: (id: string) => void;
  disabled?: boolean;
}

export const DraftList: React.FC<Props> = ({
  drafts,
  selectedIds,
  onToggleSelect,
  disabled
}) => {
  if (drafts.length === 0) {
    return (
      <div style={{
        padding: '32px 16px',
        textAlign: 'center',
        color: '#64748b',
        fontSize: '13px',
      }}>
        No drafts scanned yet. Open Gmail Drafts and click <strong>Scan Drafts</strong>.
      </div>
    );
  }

  const renderStatusBadge = (draft: DraftItem) => {
    switch (draft.status) {
      case 'SENT':
        return <span style={{ color: '#22c55e', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '3px', fontWeight: 600 }}><CheckCircle size={13} /> SENT</span>;
      case 'SENDING':
      case 'OPENING':
      case 'READY':
        return <span style={{ color: '#38bdf8', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '3px', fontWeight: 600 }}><Clock size={13} /> {draft.status}</span>;
      case 'FAILED':
        return <span style={{ color: '#ef4444', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '3px', fontWeight: 600 }}><XCircle size={13} /> FAILED</span>;
      case 'SKIPPED':
        return <span style={{ color: '#f59e0b', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '3px', fontWeight: 600 }}><AlertCircle size={13} /> SKIPPED</span>;
      case 'UNKNOWN':
        return <span style={{ color: '#a855f7', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '3px', fontWeight: 600 }}><HelpCircle size={13} /> UNKNOWN</span>;
      default:
        return null;
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      maxHeight: '260px',
      overflowY: 'auto',
      paddingRight: '4px',
    }}>
      {drafts.map((draft) => {
        const isSelected = selectedIds.includes(draft.id);

        return (
          <div
            key={draft.id}
            onClick={() => !disabled && onToggleSelect(draft.id)}
            style={{
              padding: '10px 12px',
              backgroundColor: isSelected ? '#1e293b' : '#0f172a',
              border: `1px solid ${isSelected ? '#38bdf8' : '#334155'}`,
              borderRadius: '8px',
              cursor: disabled ? 'default' : 'pointer',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px',
              transition: 'all 0.15s ease',
            }}
          >
            <input
              type="checkbox"
              checked={isSelected}
              disabled={disabled}
              onChange={() => {}}
              onClick={(e) => {
                e.stopPropagation();
                if (!disabled) {
                  onToggleSelect(draft.id);
                }
              }}
              style={{
                marginTop: '3px',
                cursor: disabled ? 'default' : 'pointer',
                accentColor: '#0284c7',
              }}
            />

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
                <div style={{
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#f8fafc',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  maxWidth: '220px',
                }}>
                  {draft.recipient || 'Draft'}
                </div>
                <div>{renderStatusBadge(draft)}</div>
              </div>

              <div style={{
                fontSize: '12px',
                color: '#cbd5e1',
                fontWeight: 500,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}>
                {draft.hasAttachment && <Paperclip size={12} color="#94a3b8" />}
                <span>{draft.subject || '(No Subject)'}</span>
              </div>

              {draft.preview && (
                <div style={{
                  fontSize: '11px',
                  color: '#64748b',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  marginTop: '2px',
                }}>
                  {draft.preview}
                </div>
              )}

              {draft.errorMessage && (
                <div style={{
                  fontSize: '11px',
                  color: '#f87171',
                  marginTop: '4px',
                  lineHeight: 1.2,
                }}>
                  {draft.errorMessage}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
