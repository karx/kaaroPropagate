import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: false,
    allowedHosts: [
      "5173--0199ad84-7027-76e5-80a1-b3d96a8105a5.us-east-1-01.gitpod.dev"
    ],
    hmr: {
      clientPort: 443
    }
  }
})
