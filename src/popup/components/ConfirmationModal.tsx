import React from 'react';
import { AlertTriangle, Send, X } from 'lucide-react';

interface Props {
  count: number;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmationModal: React.FC<Props> = ({ count, onConfirm, onCancel }) => {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.88)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      zIndex: 100,
    }}>
      <div style={{
        backgroundColor: '#1e293b',
        borderRadius: '12px',
        border: '1px solid #ef4444',
        width: '100%',
        padding: '22px',
        boxShadow: '0 25px 30px -10px rgba(0, 0, 0, 0.6)',
        textAlign: 'center',
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          backgroundColor: 'rgba(239, 68, 68, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 12px auto',
          color: '#ef4444',
        }}>
          <AlertTriangle size={28} />
        </div>

        <h3 style={{ margin: '0 0 8px 0', fontSize: '17px', color: '#f8fafc', fontWeight: 600 }}>
          Confirm Sending Batch
        </h3>

        <p style={{ margin: '0 0 18px 0', fontSize: '14px', color: '#cbd5e1', lineHeight: 1.4 }}>
          You are about to send <strong>{count}</strong> draft{count === 1 ? '' : 's'} through Gmail.
        </p>

        <div style={{
          backgroundColor: '#0f172a',
          borderRadius: '8px',
          padding: '10px',
          fontSize: '12px',
          color: '#94a3b8',
          marginBottom: '20px',
          textAlign: 'left',
          lineHeight: 1.4,
        }}>
          • Human-paced delays will be applied between sends.<br />
          • Each draft's recipient & subject are verified before clicking Send.<br />
          • You can press STOP at any time.
        </div>

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
          <button
            onClick={onCancel}
            style={{
              flex: 1,
              padding: '10px',
              backgroundColor: '#334155',
              border: 'none',
              borderRadius: '6px',
              color: '#f8fafc',
              fontSize: '13px',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
            }}
          >
            <X size={16} /> Cancel
          </button>
          <button
            onClick={onConfirm}
            style={{
              flex: 1,
              padding: '10px',
              backgroundColor: '#dc2626',
              border: 'none',
              borderRadius: '6px',
              color: '#ffffff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
            }}
          >
            <Send size={16} /> Confirm & Send
          </button>
        </div>
      </div>
    </div>
  );
};
