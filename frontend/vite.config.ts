import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/us': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/us/, ''),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => { });
        }
      },
      '/api/crypto': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/crypto/, ''),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => { });
        }
      },
      '/api/hodl': {
        target: 'http://127.0.0.1:8006',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/hodl/, ''),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => { });
        }
      },
      '/api/orchestrator': {
        target: 'http://127.0.0.1:8005',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/orchestrator/, ''),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => { });
        }
      },
      '/api/india': {
        target: 'http://127.0.0.1:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/india/, ''),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => { });
        }
      }
    }
  }
})
