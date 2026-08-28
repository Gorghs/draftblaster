import { describe, it, expect } from 'vitest';
import React from 'react';
import { renderToString } from 'react-dom/server';
import { App } from '../src/popup/App';

describe('Popup App Render Test', () => {
  it('renders without throwing exceptions', () => {
    const html = renderToString(<App />);
    expect(html).toContain('DraftBlaster');
  });
});
