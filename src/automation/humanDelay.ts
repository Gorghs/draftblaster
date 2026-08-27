/**
 * Human-paced variable delay generator.
 * Produces random delays within a specified window with natural jitter.
 */
export function getRandomDelay(minMs: number, maxMs: number): number {
  if (minMs >= maxMs) return minMs;
  return Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
}

export function humanDelay(minMs: number, maxMs: number): Promise<void> {
  const ms = getRandomDelay(minMs, maxMs);
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Delays as specified in requirements
export const STANDARD_DELAYS = {
  afterOpenDraft: () => humanDelay(1500, 3500),
  afterNavigation: () => humanDelay(1500, 4000),
  beforeSend: () => humanDelay(1000, 3000),
  afterSend: () => humanDelay(2500, 5000),
  beforeNextDraft: () => humanDelay(1500, 4000),
};
