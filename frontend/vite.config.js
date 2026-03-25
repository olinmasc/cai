import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // This ensures assets are loaded from the root, fixing the 404 errors
  base: '/',
  build: {
    // This ensures the output folder name matches what Vercel expects
    outDir: 'dist',
  }
})