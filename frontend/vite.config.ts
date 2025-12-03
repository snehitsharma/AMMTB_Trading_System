import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/us': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/us/, '')
      },
      '/api/crypto': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/crypto/, '')
      },
      '/api/india': {
        target: 'http://localhost:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/india/, '')
      },
      '/api/ai': {
        target: 'http://localhost:8004/api/v1',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ai/, '')
      },
      '/api/orchestrator': {
        target: 'http://localhost:8005/api/v1',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/orchestrator/, '')
      }
    }
  }
})
