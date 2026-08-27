import { GeminiClient } from './geminiClient';
import { AIRecommendation, AllowedAIAction } from '../types';
import { NavigationContext } from './aiSchemas';

export class GeminiNavigator {
  private client: GeminiClient;
  private attemptCounts: Map<string, number> = new Map();
  private maxAttempts: number;

  constructor(client: GeminiClient, maxAttempts: number = 2) {
    this.client = client;
    this.maxAttempts = maxAttempts;
  }

  public resetAttempts(stateKey: string = 'global') {
    this.attemptCounts.set(stateKey, 0);
  }

  public async decideRecovery(
    context: NavigationContext,
    stateKey: string = 'global'
  ): Promise<{ action?: AllowedAIAction; reason?: string; error?: string }> {
    const currentAttempts = this.attemptCounts.get(stateKey) || 0;
    if (currentAttempts >= this.maxAttempts) {
      return {
        action: 'STOP',
        reason: 'Gemini could not recover the Gmail navigation state after maximum attempts.',
        error: `Exceeded max AI recovery attempts (${this.maxAttempts}).`,
      };
    }

    this.attemptCounts.set(stateKey, currentAttempts + 1);

    const result = await this.client.getNavigationRecommendation(context);
    if (result.error || !result.recommendation) {
      return {
        action: 'STOP',
        error: result.error || 'Unknown AI recovery error',
        reason: 'AI recommendation failed or was rejected.',
      };
    }

    return {
      action: result.recommendation.action,
      reason: result.recommendation.reason,
    };
  }
}
