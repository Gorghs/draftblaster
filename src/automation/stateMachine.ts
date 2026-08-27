import { AutomationState, DraftItem, ExtensionSettings, RunState } from '../types';
import { scanDraftRows } from '../content/draftScanner';
import {
  findDraftRows,
  findDraftRow,
  findDraftsNavigation,
  findComposeWindow,
  findActiveDialog,
  GMAIL_SELECTORS,
} from '../content/gmailSelectors';
import { detectCurrentGmailState, waitForCondition } from '../content/gmailStateDetector';
import { verifyDraftBeforeSend, sendCurrentVerifiedDraft, closeCurrentDraft } from '../content/draftSender';
import { STANDARD_DELAYS, humanDelay } from './humanDelay';
import { GeminiClient } from '../ai/geminiClient';
import { GeminiNavigator } from '../ai/geminiNavigator';

export class AutomationStateMachine {
  private runState: RunState;
  private settings: ExtensionSettings;
  private onStateChange: (state: RunState) => void;
  private geminiNavigator: GeminiNavigator;
  private userConfirmed: boolean = false;

  constructor(
    initialState: RunState,
    settings: ExtensionSettings,
    onStateChange: (state: RunState) => void
  ) {
    this.runState = { ...initialState };
    this.settings = { ...settings };
    this.onStateChange = onStateChange;

    const geminiClient = new GeminiClient(
      settings.geminiApiKey,
      settings.geminiModel,
      settings.geminiMinConfidence
    );
    this.geminiNavigator = new GeminiNavigator(geminiClient, settings.maxAiRecoveryAttempts);
  }

  public updateSettings(settings: Partial<ExtensionSettings>) {
    this.settings = { ...this.settings, ...settings };
    const client = new GeminiClient(
      this.settings.geminiApiKey,
      this.settings.geminiModel,
      this.settings.geminiMinConfidence
    );
    this.geminiNavigator = new GeminiNavigator(client, this.settings.maxAiRecoveryAttempts);
  }

  private update(patch: Partial<RunState>) {
    this.runState = { ...this.runState, ...patch };
    this.onStateChange(this.runState);
  }

  public stop() {
    this.update({
      isStopRequested: true,
      state: 'STOPPED',
      statusMessage: 'Automation stopped by user.',
    });
  }

  public async scan(): Promise<DraftItem[]> {
    this.update({ state: 'SCANNING', statusMessage: 'Scanning Gmail Drafts...' });

    if (this.settings.mockMode) {
      await humanDelay(200, 400);
      const mockDrafts: DraftItem[] = [
        {
          id: 'mock-1',
          recipient: 'recruiter@techfirm.example',
          subject: 'QA Engineering Application',
          preview: 'Hello, attached is my resume for the QA position.',
          hasAttachment: true,
          isValidRecipient: true,
          status: 'PENDING',
        },
        {
          id: 'mock-2',
          recipient: 'hr@cloudstartup.example',
          subject: 'Senior QA Automation Engineer',
          preview: 'Hi hiring team, please find my application enclosed.',
          hasAttachment: true,
          isValidRecipient: true,
          status: 'PENDING',
        },
        {
          id: 'mock-3',
          recipient: 'careers@innovate.example',
          subject: 'General Inquiry - QA Lead',
          preview: 'Checking if you are still looking for QA contractors.',
          hasAttachment: false,
          isValidRecipient: true,
          status: 'PENDING',
        },
      ];

      const autoSelected = mockDrafts.slice(0, this.settings.runLimit).map((d) => d.id);

      this.update({
        state: 'DRAFT_LIST_READY',
        drafts: mockDrafts,
        selectedDraftIds: autoSelected,
        statusMessage: `Found ${mockDrafts.length} drafts in Mock Mode. ${autoSelected.length} selected.`,
      });
      return mockDrafts;
    }

    const stateCtx = detectCurrentGmailState();
    if (!stateCtx.isDraftsUrl) {
      const draftsNav = findDraftsNavigation();
      if (draftsNav) {
        draftsNav.click();
        await STANDARD_DELAYS.afterNavigation();
      }
    }

    await waitForCondition(() => scanDraftRows().length > 0, 5000);

    const drafts = scanDraftRows();
    const autoSelected = drafts.slice(0, this.settings.runLimit).map((d) => d.id);

    this.update({
      state: 'DRAFT_LIST_READY',
      drafts,
      selectedDraftIds: autoSelected,
      statusMessage: `Found ${drafts.length} drafts. ${autoSelected.length} selected for sending.`,
    });

    return drafts;
  }

  public syncRunState(stored: Partial<RunState>) {
    this.runState = {
      ...this.runState,
      ...stored,
      drafts: (stored.drafts && stored.drafts.length > 0) ? stored.drafts : this.runState.drafts,
      selectedDraftIds: (stored.selectedDraftIds && stored.selectedDraftIds.length > 0) ? stored.selectedDraftIds : this.runState.selectedDraftIds,
    };
  }

  public async startSending(draftIdsToSend?: string[]): Promise<void> {
    // ALWAYS reset stop request flag when starting a new send run
    this.runState.isStopRequested = false;
    this.userConfirmed = true;

    // Resolve target draft IDs from arguments or state
    let targetIds = (draftIdsToSend && draftIdsToSend.length > 0)
      ? draftIdsToSend
      : this.runState.selectedDraftIds;

    // If drafts list in memory is empty, try scanning live DOM
    if (this.runState.drafts.length === 0 && !this.settings.mockMode) {
      const scanned = scanDraftRows();
      if (scanned.length > 0) {
        this.runState.drafts = scanned;
      }
    }

    if (!targetIds || targetIds.length === 0) {
      targetIds = this.runState.drafts.map((d) => d.id);
    }

    const allowedDraftIds = targetIds.slice(0, this.settings.runLimit);

    if (allowedDraftIds.length === 0) {
      this.update({
        state: 'STOPPED',
        statusMessage: 'No drafts found or selected to send.',
      });
      return;
    }

    this.update({
      state: 'OPENING_DRAFT',
      selectedDraftIds: allowedDraftIds,
      totalToSend: allowedDraftIds.length,
      currentIndex: 0,
      sentCount: 0,
      failedCount: 0,
      skippedCount: 0,
      isStopRequested: false,
      statusMessage: `Starting send run for ${allowedDraftIds.length} drafts...`,
    });

    for (let i = 0; i < allowedDraftIds.length; i++) {
      if (this.runState.isStopRequested) {
        this.update({ state: 'STOPPED', statusMessage: 'Sending stopped by user.' });
        break;
      }

      const draftId = allowedDraftIds[i];
      let draft = this.runState.drafts.find((d) => d.id === draftId);
      if (!draft) {
        draft = this.runState.drafts[i] || {
          id: draftId,
          recipient: 'Draft Recipient',
          subject: '(Draft)',
          preview: '',
          hasAttachment: false,
          isValidRecipient: true,
          status: 'PENDING',
          rowIndex: i,
        };
      }

      this.update({
        currentIndex: i + 1,
        currentDraftRecipient: draft.recipient,
        currentDraftSubject: draft.subject,
        statusMessage: `Processing draft ${i + 1} of ${allowedDraftIds.length}: ${draft.subject}`,
      });

      // Ensure we are back on the main Drafts list before processing next draft
      if (!this.settings.mockMode) {
        await this.ensureOnDraftsList();
      }

      const result = await this.processSingleDraft(draft, i);
      if (result.stopped) {
        break;
      }

      if (result.status === 'SENT') {
        this.update({ sentCount: this.runState.sentCount + 1 });
      } else if (result.status === 'SKIPPED') {
        this.update({ skippedCount: this.runState.skippedCount + 1 });
      } else {
        this.update({ failedCount: this.runState.failedCount + 1 });
      }

      if (i < allowedDraftIds.length - 1 && !this.runState.isStopRequested) {
        this.update({
          state: 'NEXT_DRAFT',
          statusMessage: `Waiting before opening next draft...`,
        });
        if (this.settings.mockMode) {
          await humanDelay(100, 200);
        } else {
          await STANDARD_DELAYS.beforeNextDraft();
        }
      }
    }

    if (!this.runState.isStopRequested) {
      this.update({
        state: 'COMPLETED',
        statusMessage: `Run completed! Sent: ${this.runState.sentCount}, Failed: ${this.runState.failedCount}`,
      });
    }
  }

  private async ensureOnDraftsList(): Promise<void> {
    // If a compose window is currently lingering, close it
    if (findComposeWindow()) {
      await closeCurrentDraft();
    }

    const stateCtx = detectCurrentGmailState();
    if (!stateCtx.isDraftsUrl || findDraftRows().length === 0) {
      const draftsNav = findDraftsNavigation();
      if (draftsNav) {
        draftsNav.click();
      } else {
        window.location.hash = '#drafts';
      }
      await waitForCondition(() => findDraftRows().length > 0, 5000);
      await STANDARD_DELAYS.afterNavigation();
    }
  }

  private async processSingleDraft(draft: DraftItem, fallbackIndex: number): Promise<{ status: DraftItem['status']; stopped?: boolean }> {
    this.markDraftStatus(draft.id, 'OPENING');
    this.update({ state: 'OPENING_DRAFT', statusMessage: `Opening draft for ${draft.recipient}...` });

    if (this.settings.mockMode) {
      await humanDelay(100, 200);
      if (this.runState.isStopRequested) return { status: 'STOPPED', stopped: true };

      this.markDraftStatus(draft.id, 'READY');
      this.update({ state: 'VALIDATING', statusMessage: `Validating draft details for ${draft.recipient}...` });
      await humanDelay(100, 200);

      if (this.runState.isStopRequested) return { status: 'STOPPED', stopped: true };

      this.markDraftStatus(draft.id, 'SENDING');
      this.update({ state: 'SENDING', statusMessage: `Sending draft to ${draft.recipient}...` });
      await humanDelay(100, 200);

      if (this.runState.isStopRequested) return { status: 'STOPPED', stopped: true };

      this.markDraftStatus(draft.id, 'SENT');
      this.update({ state: 'SEND_CONFIRMED', statusMessage: `Draft sent to ${draft.recipient}.` });
      await humanDelay(100, 200);
      return { status: 'SENT' };
    }

    let row = findDraftRow({ subject: draft.subject, recipient: draft.recipient, rowIndex: draft.rowIndex ?? fallbackIndex });
    if (!row) {
      if (this.settings.geminiEnabled) {
        const recovered = await this.triggerAIRecovery('Cannot find draft row in list', 'DRAFTS_PAGE');
        if (!recovered) {
          this.markDraftStatus(draft.id, 'FAILED', 'Draft row could not be located in Gmail list.');
          return { status: 'FAILED' };
        }
        row = findDraftRow({ subject: draft.subject, recipient: draft.recipient, rowIndex: draft.rowIndex ?? fallbackIndex });
      }
    }

    if (!row) {
      this.markDraftStatus(draft.id, 'FAILED', 'Draft row not found in list.');
      return { status: 'FAILED' };
    }

    // Trigger natural click sequence on the draft row / subject link
    const clickTarget = (row.querySelector('span.bog, span.bqe, td.xY, [role="link"]') as HTMLElement) || row;
    clickTarget.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
    clickTarget.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
    clickTarget.click();
    await STANDARD_DELAYS.afterOpenDraft();

    if (this.runState.isStopRequested) return { status: 'STOPPED', stopped: true };

    let composeOpened = await waitForCondition(() => findComposeWindow() !== null, 3500);
    if (!composeOpened) {
      // Retry clicking once
      clickTarget.click();
      composeOpened = await waitForCondition(() => findComposeWindow() !== null, 3500);
    }

    if (!composeOpened) {
      if (this.settings.geminiEnabled) {
        await this.triggerAIRecovery('Draft compose window failed to open', 'DRAFT_OPEN');
      }
      if (!findComposeWindow()) {
        this.markDraftStatus(draft.id, 'FAILED', 'Compose window failed to open for draft.');
        return { status: 'FAILED' };
      }
    }

    this.markDraftStatus(draft.id, 'READY');
    this.update({ state: 'VALIDATING', statusMessage: `Validating open draft for ${draft.recipient}...` });

    const verification = verifyDraftBeforeSend(draft, this.userConfirmed);
    if (!verification.canSend) {
      await closeCurrentDraft();
      this.markDraftStatus(draft.id, 'FAILED', `Validation failed: ${verification.reason}`);
      return { status: 'FAILED' };
    }

    if (this.runState.isStopRequested) {
      await closeCurrentDraft();
      return { status: 'STOPPED', stopped: true };
    }

    this.markDraftStatus(draft.id, 'SENDING');
    this.update({ state: 'SENDING', statusMessage: `Sending draft...` });

    const sendResult = await sendCurrentVerifiedDraft();

    if (sendResult.status === 'SENT') {
      this.markDraftStatus(draft.id, 'SENT');
      this.update({ state: 'SEND_CONFIRMED', statusMessage: `Successfully sent!` });
      return { status: 'SENT' };
    } else if (sendResult.status === 'UNKNOWN') {
      this.markDraftStatus(draft.id, 'UNKNOWN', sendResult.error || 'Ambiguous send result; automatic retry prevented to avoid duplicates.');
      return { status: 'UNKNOWN' };
    } else {
      await closeCurrentDraft();
      this.markDraftStatus(draft.id, 'FAILED', sendResult.error || 'Failed to send draft.');
      return { status: 'FAILED' };
    }
  }

  private markDraftStatus(id: string, status: DraftItem['status'], errorMessage?: string) {
    const updated = this.runState.drafts.map((d) => {
      if (d.id === id) {
        return { ...d, status, errorMessage };
      }
      return d;
    });
    this.update({ drafts: updated });
  }

  private async triggerAIRecovery(reason: string, expectedState: string): Promise<boolean> {
    this.update({
      state: 'AI_RECOVERY',
      statusMessage: `AI Recovery: Analyzing Gmail state with Gemini (${reason})...`,
    });

    const currentUrl = window.location.href;
    const dialog = findActiveDialog();
    const visibleText = (document.body.innerText || '').slice(0, 1500);

    const { action, error } = await this.geminiNavigator.decideRecovery({
      url: currentUrl,
      automationState: this.runState.state,
      expectedState,
      visibleTextSummary: visibleText,
      dialogPresent: dialog !== null,
      dialogTitle: dialog?.getAttribute('aria-label') || undefined,
      errorMessage: reason,
    });

    if (error || !action || action === 'STOP') {
      this.update({
        state: 'ERROR',
        errorMessage: error || 'AI navigation recovery aborted or failed.',
        statusMessage: 'Gemini could not recover the Gmail navigation state.',
      });
      return false;
    }

    return await this.executeSafeAIAction(action);
  }

  private async executeSafeAIAction(action: string): Promise<boolean> {
    switch (action) {
      case 'OPEN_DRAFTS':
      case 'RETURN_TO_DRAFTS': {
        const nav = findDraftsNavigation();
        if (nav) {
          nav.click();
          await STANDARD_DELAYS.afterNavigation();
          return true;
        }
        window.location.hash = '#drafts';
        await STANDARD_DELAYS.afterNavigation();
        return true;
      }
      case 'CLOSE_DIALOG': {
        const dialog = findActiveDialog();
        const closeBtn = dialog?.querySelector('button[aria-label*="Close" i], [aria-label*="Cancel" i], button') as HTMLElement;
        if (closeBtn) {
          closeBtn.click();
          await humanDelay(1000, 2000);
          return true;
        }
        return false;
      }
      case 'GO_BACK': {
        window.history.back();
        await STANDARD_DELAYS.afterNavigation();
        return true;
      }
      case 'REFRESH': {
        window.location.reload();
        await humanDelay(3000, 5000);
        return true;
      }
      case 'WAIT':
      case 'RETRY': {
        await humanDelay(2000, 4000);
        return true;
      }
      default:
        return false;
    }
  }
}
