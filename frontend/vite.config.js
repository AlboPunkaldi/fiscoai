import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // ^/   = inizio stringa.  Qualsiasi URL che comincia con
      // /auth   /invoices   /tax   /chat   viene inoltrato
      '^/(auth|invoices|tax|chat)': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});