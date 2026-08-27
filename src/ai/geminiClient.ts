import { AIRecommendation } from '../types';
import { NavigationContext } from './aiSchemas';
import { validateAIRecommendation } from './aiActionValidator';

export class GeminiClient {
  private apiKey: string;
  private model: string;
  private minConfidence: number;

  constructor(apiKey: string, model: string = 'gemini-2.5-flash', minConfidence: number = 0.70) {
    this.apiKey = apiKey.trim();
    this.model = model.trim() || 'gemini-2.5-flash';
    this.minConfidence = minConfidence;
  }

  public updateConfig(apiKey: string, model: string, minConfidence: number) {
    this.apiKey = apiKey.trim();
    this.model = model.trim() || 'gemini-2.5-flash';
    this.minConfidence = minConfidence;
  }

  public async getNavigationRecommendation(context: NavigationContext): Promise<{
    recommendation?: AIRecommendation;
    error?: string;
  }> {
    if (!this.apiKey) {
      return { error: 'Gemini API Key is not configured.' };
    }

    const systemInstruction = `You are an AI navigation assistant for Gmail automation inside a browser extension.
When the deterministic state machine gets stuck, you analyze the current DOM context and recommend the next SAFE navigation action.
You MUST output ONLY valid JSON matching this schema:
{
  "action": "OPEN_DRAFTS" | "OPEN_SELECTED_DRAFT" | "RETURN_TO_DRAFTS" | "GO_BACK" | "REFRESH" | "WAIT" | "CLOSE_DIALOG" | "RETRY" | "STOP",
  "confidence": number between 0.0 and 1.0,
  "reason": "concise explanation"
}

CRITICAL RULES:
- NEVER recommend any SEND action. You cannot trigger sending.
- Only choose from the allowed actions above.
- If unsure or state is unrecoverable, return "STOP" or "RETRY".`;

    const userPrompt = `Gmail Navigation State Analysis:
- Current URL: ${context.url}
- Automation State: ${context.automationState}
- Expected State: ${context.expectedState}
- Dialog Present: ${context.dialogPresent ? 'Yes: ' + (context.dialogTitle || 'Unknown') : 'No'}
- Error Encountered: ${context.errorMessage || 'None'}
- Sanitized Visible Text / DOM Context:
${context.visibleTextSummary || 'No summary available'}

What navigation action should the extension take? Return strict JSON.`;

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${this.model}:generateContent?key=${this.apiKey}`;

    const requestBody = {
      contents: [
        {
          role: 'user',
          parts: [{ text: userPrompt }],
        },
      ],
      systemInstruction: {
        parts: [{ text: systemInstruction }],
      },
      generationConfig: {
        responseMimeType: 'application/json',
        temperature: 0.1,
      },
    };

    try {
      // Direct client-side HTTPS request
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errMsg = `Gemini API HTTP ${response.status}`;
        try {
          const parsedErr = JSON.parse(errorText);
          if (parsedErr.error?.message) {
            errMsg += `: ${parsedErr.error.message}`;
          }
        } catch {
          errMsg += `: ${errorText.slice(0, 100)}`;
        }
        return { error: errMsg };
      }

      const json = await response.json();
      const rawText = json.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!rawText) {
        return { error: 'Gemini returned empty candidate response' };
      }

      let parsedPayload: any;
      try {
        parsedPayload = JSON.parse(rawText.trim());
      } catch (parseErr: any) {
        return { error: `Failed to parse Gemini JSON: ${parseErr.message}` };
      }

      const validation = validateAIRecommendation(parsedPayload, this.minConfidence);
      if (!validation.isValid || !validation.action) {
        return { error: `AI recommendation rejected: ${validation.rejectionReason}` };
      }

      return {
        recommendation: {
          action: validation.action,
          confidence: validation.confidence || 0,
          reason: validation.reason || '',
        },
      };
    } catch (err: any) {
      return { error: `Network error contacting Gemini: ${err.message || String(err)}` };
    }
  }
}
