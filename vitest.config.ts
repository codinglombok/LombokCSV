import { defineConfig } from 'vitest/config';

// S4 / DELTA A: the reference implementation is held to 95% statement and 90%
// branch coverage. The per-port CI gate stays at 90% (LombokVector pattern).
export default defineConfig({
  test: {
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      reporter: ['text', 'lcov'],
      thresholds: { lines: 95, functions: 95, branches: 90, statements: 95 },
    },
  },
});
