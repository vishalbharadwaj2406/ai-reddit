import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'happy-dom',
    globals: true,
    // setupFiles: ['./tests/setup.ts'], // Commented out to avoid path issues
  },
});
