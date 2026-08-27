import { describe, it, expect } from 'vitest';
import { AutomationStateMachine } from '../src/automation/stateMachine';
import { DEFAULT_SETTINGS } from '../src/storage/settings';
import { INITIAL_RUN_STATE } from '../src/storage/runState';

describe('DraftBlaster State Machine & Safety Logic Tests', () => {
  it('should scan drafts in mock mode and auto-select all found drafts up to run limit', async () => {
    const updates: any[] = [];
    const sm = new AutomationStateMachine(
      INITIAL_RUN_STATE,
      { ...DEFAULT_SETTINGS, mockMode: true },
      (state) => updates.push(state)
    );

    const drafts = await sm.scan();
    expect(drafts.length).toBe(3);
    
    const lastUpdate = updates[updates.length - 1];
    expect(lastUpdate.state).toBe('DRAFT_LIST_READY');
    expect(lastUpdate.selectedDraftIds.length).toBe(3);
  });

  it('should enforce run limit correctly', async () => {
    const updates: any[] = [];
    const sm = new AutomationStateMachine(
      INITIAL_RUN_STATE,
      { ...DEFAULT_SETTINGS, mockMode: true, runLimit: 1 },
      (state) => updates.push(state)
    );

    await sm.scan();
    const lastState = updates[updates.length - 1];
    expect(lastState.selectedDraftIds.length).toBe(1);
  });

  it('should process sending and honor STOP command immediately', async () => {
    const updates: any[] = [];
    const sm = new AutomationStateMachine(
      INITIAL_RUN_STATE,
      { ...DEFAULT_SETTINGS, mockMode: true },
      (state) => updates.push(state)
    );

    await sm.scan();
    
    const sendPromise = sm.startSending(['mock-1', 'mock-2']);
    
    setTimeout(() => {
      sm.stop();
    }, 100);

    await sendPromise;

    const finalState = updates[updates.length - 1];
    expect(finalState.isStopRequested).toBe(true);
    expect(finalState.state).toBe('STOPPED');
  });

  it('should default to 500 runLimit threshold and complete batch sending', async () => {
    expect(DEFAULT_SETTINGS.runLimit).toBe(500);

    const updates: any[] = [];
    const sm = new AutomationStateMachine(
      INITIAL_RUN_STATE,
      { ...DEFAULT_SETTINGS, mockMode: true },
      (state) => updates.push(state)
    );

    await sm.scan();
    await sm.startSending(['mock-1', 'mock-2', 'mock-3']);

    const finalState = updates[updates.length - 1];
    expect(finalState.state).toBe('COMPLETED');
    expect(finalState.sentCount).toBe(3);
    expect(finalState.failedCount).toBe(0);
  });
});
