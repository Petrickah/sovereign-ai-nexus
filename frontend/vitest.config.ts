import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// Separate from vite.config.ts: that file wires the react-compiler babel
// plugin and the dev-only /chat, /history proxy, neither of which the test
// environment needs or should depend on.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
  },
})
